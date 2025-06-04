import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeScraper:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.max_results = 50
        
    def search_channels_by_keywords(self, keywords_file):
        """キーワードファイルからチャンネルを検索"""
        with open(keywords_file, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        
        all_channels = []
        
        for keyword in keywords:
            try:
                search_response = self.youtube.search().list(
                    q=keyword,
                    type='channel',
                    part='id,snippet',
                    maxResults=self.max_results,
                    relevanceLanguage='en'
                ).execute()
                
                for item in search_response.get('items', []):
                    channel_id = item['id']['channelId']
                    channel_info = self.get_channel_details(channel_id)
                    
                    if channel_info and self.meets_criteria(channel_info):
                        channel_info['keyword'] = keyword
                        all_channels.append(channel_info)
                        
            except HttpError as e:
                print(f"キーワード '{keyword}' の検索でエラー: {e}")
                continue
                
        return self.remove_duplicates(all_channels)
    
    def get_channel_details(self, channel_id):
        """チャンネルの詳細情報を取得"""
        try:
            channel_response = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return None
                
            channel = channel_response['items'][0]
            
            # アップロードプレイリストIDを取得
            uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
            
            # 動画リストを取得
            videos = self.get_channel_videos(uploads_playlist_id)
            
            # 拡散率の高い動画を計算
            high_spread_videos = self.calculate_spread_rate(videos)
            
            return {
                'channel_id': channel_id,
                'channel_name': channel['snippet']['title'],
                'channel_url': f'https://www.youtube.com/channel/{channel_id}',
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'created_date': channel['snippet']['publishedAt'],
                'videos': videos,
                'high_spread_videos': high_spread_videos,
                'is_faceless': self.check_faceless(channel, videos)
            }
            
        except HttpError as e:
            print(f"チャンネル {channel_id} の詳細取得でエラー: {e}")
            return None
    
    def get_channel_videos(self, playlist_id, max_videos=50):
        """チャンネルの動画リストを取得"""
        videos = []
        next_page_token = None
        
        try:
            while len(videos) < max_videos:
                playlist_response = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=min(50, max_videos - len(videos)),
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response.get('items', []):
                    video_id = item['contentDetails']['videoId']
                    video_details = self.get_video_details(video_id)
                    if video_details:
                        videos.append(video_details)
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
                    
        except HttpError as e:
            print(f"プレイリスト {playlist_id} の動画取得でエラー: {e}")
            
        return videos
    
    def get_video_details(self, video_id):
        """動画の詳細情報を取得"""
        try:
            video_response = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                return None
                
            video = video_response['items'][0]
            
            return {
                'video_id': video_id,
                'title': video['snippet']['title'],
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'views': int(video['statistics'].get('viewCount', 0)),
                'likes': int(video['statistics'].get('likeCount', 0)),
                'published_at': video['snippet']['publishedAt'],
                'thumbnail': video['snippet']['thumbnails']['default']['url']
            }
            
        except HttpError:
            return None
    
    def calculate_spread_rate(self, videos):
        """拡散率の高い動画を計算（再生数 / 登録者数）"""
        high_spread_videos = []
        
        for video in videos:
            if video.get('views', 0) > 0:
                # この時点では登録者数がないので、後で計算
                high_spread_videos.append(video)
                
        return high_spread_videos
    
    def meets_criteria(self, channel_info):
        """チャンネルが条件を満たすかチェック"""
        # 登録者数2万人以下
        if channel_info['subscriber_count'] > 20000:
            return False
            
        # 投稿数30本以内
        if channel_info['video_count'] > 30:
            return False
            
        # チャンネル開設から2ヶ月以内
        created_date = datetime.fromisoformat(channel_info['created_date'].replace('Z', '+00:00'))
        two_months_ago = datetime.now(created_date.tzinfo) - timedelta(days=60)
        if created_date < two_months_ago:
            return False
            
        # 拡散率3〜8の動画が3本以上
        spread_rate_videos = []
        for video in channel_info['videos']:
            if channel_info['subscriber_count'] > 0:
                spread_rate = video['views'] / channel_info['subscriber_count']
                if 3 <= spread_rate <= 8:
                    spread_rate_videos.append({
                        **video,
                        'spread_rate': spread_rate
                    })
                    
        if len(spread_rate_videos) < 3:
            return False
            
        # 拡散率の高い動画トップ3を保存
        channel_info['high_spread_videos'] = sorted(
            spread_rate_videos, 
            key=lambda x: x['spread_rate'], 
            reverse=True
        )[:3]
        
        return True
    
    def check_faceless(self, channel, videos):
        """顔出しが目立たないチャンネルかチェック"""
        faceless_keywords = [
            'animation', 'animated', 'cartoon', 'whiteboard',
            'tutorial', 'screen recording', 'gameplay', 'compilation',
            'text', 'infographic', 'documentary', 'nature',
            'timelapse', 'stock', 'footage', 'slideshow'
        ]
        
        # チャンネル名と説明文をチェック
        channel_text = (channel['snippet']['title'] + ' ' + 
                       channel['snippet'].get('description', '')).lower()
        
        for keyword in faceless_keywords:
            if keyword in channel_text:
                return True
                
        # 動画タイトルをチェック
        video_titles = ' '.join([v['title'].lower() for v in videos[:10]])
        for keyword in faceless_keywords:
            if keyword in video_titles:
                return True
                
        return False
    
    def remove_duplicates(self, channels):
        """重複チャンネルを削除"""
        unique_channels = {}
        for channel in channels:
            channel_id = channel['channel_id']
            if channel_id not in unique_channels:
                unique_channels[channel_id] = channel
                
        return list(unique_channels.values())