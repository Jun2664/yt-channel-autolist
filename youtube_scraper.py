import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeScraper:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.channels_data = []
        
    def search_channels_by_keyword(self, keyword, max_results=50):
        """キーワードでチャンネルを検索"""
        try:
            search_response = self.youtube.search().list(
                q=keyword,
                type='channel',
                part='snippet',
                maxResults=max_results,
                order='date'
            ).execute()
            
            channel_ids = [item['id']['channelId'] for item in search_response.get('items', [])]
            return channel_ids
        except HttpError as e:
            print(f"エラーが発生しました: {e}")
            return []
    
    def get_channel_details(self, channel_id):
        """チャンネルの詳細情報を取得"""
        try:
            channel_response = self.youtube.channels().list(
                id=channel_id,
                part='snippet,statistics,contentDetails'
            ).execute()
            
            if not channel_response['items']:
                return None
                
            channel = channel_response['items'][0]
            return {
                'id': channel_id,
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', ''),
                'publishedAt': channel['snippet']['publishedAt'],
                'thumbnails': channel['snippet']['thumbnails'],
                'subscriberCount': int(channel['statistics'].get('subscriberCount', 0)),
                'videoCount': int(channel['statistics'].get('videoCount', 0)),
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
            }
        except HttpError as e:
            print(f"チャンネル詳細取得エラー: {e}")
            return None
    
    def get_channel_videos(self, playlist_id, max_results=50):
        """チャンネルの動画リストを取得"""
        videos = []
        try:
            playlist_response = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part='contentDetails',
                maxResults=max_results
            ).execute()
            
            video_ids = [item['contentDetails']['videoId'] for item in playlist_response.get('items', [])]
            
            if video_ids:
                videos_response = self.youtube.videos().list(
                    id=','.join(video_ids),
                    part='snippet,statistics'
                ).execute()
                
                for video in videos_response.get('items', []):
                    videos.append({
                        'id': video['id'],
                        'title': video['snippet']['title'],
                        'publishedAt': video['snippet']['publishedAt'],
                        'viewCount': int(video['statistics'].get('viewCount', 0)),
                        'likeCount': int(video['statistics'].get('likeCount', 0)),
                        'commentCount': int(video['statistics'].get('commentCount', 0)),
                        'thumbnails': video['snippet']['thumbnails']
                    })
            
            return videos
        except HttpError as e:
            print(f"動画リスト取得エラー: {e}")
            return []
    
    def calculate_diffusion_rate(self, view_count, subscriber_count):
        """拡散率を計算"""
        if subscriber_count == 0:
            return 0
        return view_count / subscriber_count
    
    def check_personal_branding(self, channel_data, videos):
        """属人性の判定（ルールベース）"""
        personal_keywords = [
            'face', 'selfie', 'vlog', 'my', '私', 'me', 'personal',
            'daily', 'routine', 'life', 'grwm', 'day in my life'
        ]
        
        # チャンネル名とdescriptionをチェック
        channel_text = (channel_data['title'] + ' ' + channel_data['description']).lower()
        
        # サムネイルURLをチェック（顔出しを示唆するキーワード）
        thumbnail_text = json.dumps(channel_data['thumbnails']).lower()
        
        # 動画タイトルをチェック
        video_titles = ' '.join([video['title'].lower() for video in videos[:10]])
        
        all_text = channel_text + ' ' + thumbnail_text + ' ' + video_titles
        
        personal_score = sum(1 for keyword in personal_keywords if keyword in all_text)
        
        # スコアが3以上なら属人性が高いと判定
        return personal_score < 3
    
    def filter_channel(self, channel_data, videos):
        """チャンネルをフィルタリング"""
        # 条件1: 登録者数2万人以下
        if channel_data['subscriberCount'] > 20000:
            return False
            
        # 条件2: 投稿数30本以内
        if channel_data['videoCount'] > 30:
            return False
            
        # 条件3: チャンネル開設から2ヶ月以内
        created_date = datetime.fromisoformat(channel_data['publishedAt'].replace('Z', '+00:00'))
        two_months_ago = datetime.now(created_date.tzinfo) - timedelta(days=60)
        if created_date < two_months_ago:
            return False
            
        # 条件4: 拡散率3〜8の動画が3本以上
        high_diffusion_videos = []
        for video in videos:
            diffusion_rate = self.calculate_diffusion_rate(
                video['viewCount'], 
                channel_data['subscriberCount']
            )
            if 3 <= diffusion_rate <= 8:
                high_diffusion_videos.append(video)
                
        if len(high_diffusion_videos) < 3:
            return False
            
        # 条件5: 属人性が低い
        if not self.check_personal_branding(channel_data, videos):
            return False
            
        # フィルタを通過したチャンネルデータを保存
        channel_data['high_diffusion_videos'] = high_diffusion_videos[:3]
        channel_data['is_personal'] = False
        
        return True
    
    def process_keyword(self, keyword):
        """キーワードごとに処理を実行"""
        print(f"キーワード '{keyword}' で検索中...")
        channel_ids = self.search_channels_by_keyword(keyword)
        
        for channel_id in channel_ids:
            channel_data = self.get_channel_details(channel_id)
            if not channel_data:
                continue
                
            videos = self.get_channel_videos(channel_data['uploads_playlist_id'])
            
            if self.filter_channel(channel_data, videos):
                channel_data['search_keyword'] = keyword
                self.channels_data.append(channel_data)
                print(f"  ✓ {channel_data['title']} が条件を満たしました")
    
    def get_filtered_channels(self):
        """フィルタリングされたチャンネルデータを返す"""
        return self.channels_data