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
        """属人性の判定（ルールベース）- 属人性が低い場合True、高い場合Falseを返す"""
        reasons = []
        score = 0
        
        # 拡張した個人キーワードリスト
        personal_keywords = [
            'face', 'selfie', 'man', 'woman', 'boy', 'girl', 'host', 'actor', 
            'vlog', 'interview', 'my', 'me', 'personal', 'daily', 'routine', 
            'life', 'grwm', 'day in my life', '私', '僕', '俺', '自分', 
            'わたし', 'ぼく', 'おれ'
        ]
        
        channel_title = channel_data['title']
        channel_description = channel_data.get('description', '')
        
        # チャンネル名パターンチェック
        if any(pattern in channel_title for pattern in ['の部屋', 'チャンネル', 'TV', 'ch', 'Ch', 'CH']):
            score += 3
            reasons.append("チャンネル名に人名パターン")
        
        # チャンネル名とdescriptionをチェック
        channel_text = (channel_title + ' ' + channel_description).lower()
        
        # 個人キーワードチェック
        found_keywords = []
        for keyword in personal_keywords:
            if keyword in channel_text:
                score += 2
                found_keywords.append(keyword)
        
        if found_keywords:
            reasons.append(f"キーワード検出: {', '.join(found_keywords[:3])}")
        
        # 説明文の一人称チェック（日本語）
        first_person_count = sum(1 for word in ['私', '僕', '俺', '自分', 'わたし', 'ぼく', 'おれ'] 
                                if word in channel_description)
        if first_person_count >= 3:
            score += 3
            reasons.append("一人称が頻出")
        elif first_person_count >= 1:
            score += 1
            reasons.append("一人称を含む")
        
        # 動画タイトルをチェック
        video_titles = ' '.join([video['title'].lower() for video in videos[:10]])
        video_keywords_found = []
        for keyword in personal_keywords:
            if keyword in video_titles:
                score += 1
                video_keywords_found.append(keyword)
        
        if video_keywords_found:
            reasons.append(f"動画タイトルに: {', '.join(set(video_keywords_found[:3]))}")
        
        # サムネイルに人物が含まれている動画の割合をチェック（タイトルから推測）
        human_thumbnail_keywords = ['face', 'selfie', '顔', 'vlog', 'reaction', 'リアクション']
        videos_with_humans = sum(1 for v in videos[:10] 
                               if any(kw in v['title'].lower() for kw in human_thumbnail_keywords))
        
        if videos_with_humans >= 8:  # 80%以上
            score += 3
            reasons.append("全動画に人物サムネイル推定")
        elif videos_with_humans >= 5:  # 50%以上
            score += 1
            reasons.append("半数以上に人物サムネイル推定")
        
        # 判定理由を保存
        channel_data['personal_branding_score'] = min(score, 10)
        channel_data['personal_branding_reasons'] = ' + '.join(reasons) if reasons else "属人性なし"
        
        # スコアが3以上なら属人性が高いと判定（Falseを返す）
        return score < 3
    
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
        is_low_personal = self.check_personal_branding(channel_data, videos)
        if not is_low_personal:
            return False
            
        # フィルタを通過したチャンネルデータを保存
        channel_data['high_diffusion_videos'] = high_diffusion_videos[:3]
        channel_data['is_personal'] = channel_data['personal_branding_score'] >= 3
        
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