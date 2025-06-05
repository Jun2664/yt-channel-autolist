import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from channel_sources import ChannelSources
from keyword_extractor import KeywordExtractor
from keyword_research_api import KeywordResearchAPI

class YouTubeScraper:
    def __init__(self, api_key: str, region: str = 'JP', config: Dict = None, api_keys: Dict = None):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.region = region
        self.config = config or {}
        self.channels_data = []
        self.keyword_metrics = []
        
        # Initialize helper modules
        self.channel_sources = ChannelSources(api_key)
        self.keyword_extractor = KeywordExtractor(self.config.get('language', 'en'))
        
        # Initialize keyword research API
        if api_keys:
            self.keyword_api = KeywordResearchAPI(
                vidiq_key=api_keys.get('vidiq', ''),
                tubebuddy_key=api_keys.get('tubebuddy', ''),
                keywordtool_key=api_keys.get('keywordtool', '')
            )
        else:
            self.keyword_api = KeywordResearchAPI()
        
    def search_channels_by_keyword(self, keyword: str, max_results: int = 50) -> List[str]:
        """Search channels by keyword"""
        try:
            # For overseas markets, use channel sources module
            if self.region != 'JP':
                # Get channels from multiple sources
                channel_ids = set()
                
                # Search by keyword with date filter
                rising_channels = self.channel_sources.search_rising_channels(
                    [keyword], 
                    self.region,
                    datetime.now() - timedelta(days=self.config.get('channel_age_days', 60))
                )
                channel_ids.update(rising_channels)
                
                # Also get trending channels in the region
                trending_channels = self.channel_sources.get_trending_channels(self.region)
                channel_ids.update(trending_channels)
                
                return list(channel_ids)[:max_results]
            else:
                # Original Japanese implementation
                search_response = self.youtube.search().list(
                    q=keyword,
                    type='channel',
                    part='snippet',
                    maxResults=max_results,
                    order='date',
                    regionCode=self.region
                ).execute()
                
                channel_ids = [item['id']['channelId'] for item in search_response.get('items', [])]
                return channel_ids
        except HttpError as e:
            print(f"Error occurred: {e}")
            return []
    
    def get_channel_details(self, channel_id: str) -> Optional[Dict]:
        """Get channel details"""
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
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads'],
                'region': self.region
            }
        except HttpError as e:
            print(f"Error getting channel details: {e}")
            return None
    
    def get_channel_videos(self, playlist_id: str, max_results: int = 50) -> List[Dict]:
        """Get channel video list"""
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
            print(f"Error getting video list: {e}")
            return []
    
    def calculate_diffusion_rate(self, view_count: int, subscriber_count: int) -> float:
        """Calculate diffusion rate"""
        if subscriber_count == 0:
            return 0
        return view_count / subscriber_count
    
    def check_personal_branding(self, channel_data: Dict, videos: List[Dict]) -> bool:
        """Check personal branding (rule-based) - Returns True if low personal branding, False if high"""
        reasons = []
        score = 0
        
        # Extended personal keyword list with region-specific terms
        personal_keywords = [
            'face', 'selfie', 'man', 'woman', 'boy', 'girl', 'host', 'actor', 
            'vlog', 'interview', 'my', 'me', 'personal', 'daily', 'routine', 
            'life', 'grwm', 'day in my life'
        ]
        
        # Add language-specific keywords
        if self.config.get('language') == 'ja':
            personal_keywords.extend(['私', '僕', '俺', '自分', 'わたし', 'ぼく', 'おれ'])
        elif self.config.get('language') == 'es':
            personal_keywords.extend(['yo', 'mi', 'mío', 'mía'])
        elif self.config.get('language') == 'pt':
            personal_keywords.extend(['eu', 'meu', 'minha'])
        
        channel_title = channel_data['title']
        channel_description = channel_data.get('description', '')
        
        # Check channel name patterns
        personal_patterns = {
            'ja': ['の部屋', 'チャンネル', 'TV', 'ch', 'Ch', 'CH'],
            'en': ['vlog', 'life', 'diary', 'personal'],
            'es': ['vida', 'diario', 'personal'],
            'pt': ['vida', 'diário', 'pessoal']
        }
        
        lang = self.config.get('language', 'en')
        patterns = personal_patterns.get(lang, personal_patterns['en'])
        
        if any(pattern in channel_title for pattern in patterns):
            score += 3
            reasons.append("Personal pattern in channel name")
        
        # Check channel name and description
        channel_text = (channel_title + ' ' + channel_description).lower()
        
        # Personal keyword check
        found_keywords = []
        for keyword in personal_keywords:
            if keyword in channel_text:
                score += 2
                found_keywords.append(keyword)
        
        if found_keywords:
            reasons.append(f"Keywords detected: {', '.join(found_keywords[:3])}")
        
        # Check first person pronouns in description
        first_person_keywords = {
            'ja': ['私', '僕', '俺', '自分', 'わたし', 'ぼく', 'おれ'],
            'en': ['i', 'me', 'my', 'myself'],
            'es': ['yo', 'mi', 'mío'],
            'pt': ['eu', 'meu', 'minha']
        }
        
        first_person = first_person_keywords.get(lang, first_person_keywords['en'])
        first_person_count = sum(1 for word in first_person if word in channel_description.lower())
        
        if first_person_count >= 3:
            score += 3
            reasons.append("Frequent first person usage")
        elif first_person_count >= 1:
            score += 1
            reasons.append("Contains first person")
        
        # Check video titles
        video_titles = ' '.join([video['title'].lower() for video in videos[:10]])
        video_keywords_found = []
        for keyword in personal_keywords:
            if keyword in video_titles:
                score += 1
                video_keywords_found.append(keyword)
        
        if video_keywords_found:
            reasons.append(f"In video titles: {', '.join(set(video_keywords_found[:3]))}")
        
        # Check for human thumbnails (estimated from titles)
        human_thumbnail_keywords = ['face', 'selfie', 'vlog', 'reaction'] + (
            ['顔', 'リアクション'] if lang == 'ja' else []
        )
        videos_with_humans = sum(1 for v in videos[:10] 
                               if any(kw in v['title'].lower() for kw in human_thumbnail_keywords))
        
        if videos_with_humans >= 8:  # 80% or more
            score += 3
            reasons.append("All videos likely have human thumbnails")
        elif videos_with_humans >= 5:  # 50% or more
            score += 1
            reasons.append("Half or more videos likely have human thumbnails")
        
        # Save judgment reasons
        channel_data['personal_branding_score'] = min(score, 10)
        channel_data['personal_branding_reasons'] = ' + '.join(reasons) if reasons else "No personal branding"
        
        # Score of 3 or higher indicates high personal branding (return False)
        return score < 3
    
    def filter_channel(self, channel_data: Dict, videos: List[Dict]) -> bool:
        """Filter channels based on criteria"""
        # Condition 1: Subscriber count within limit
        if channel_data['subscriberCount'] > self.config.get('max_subs', 20000):
            return False
            
        # Condition 2: Video count within limit
        if channel_data['videoCount'] > self.config.get('max_videos', 30):
            return False
            
        # Condition 3: Channel created within specified days
        created_date = datetime.fromisoformat(channel_data['publishedAt'].replace('Z', '+00:00'))
        age_limit = datetime.now(created_date.tzinfo) - timedelta(days=self.config.get('channel_age_days', 60))
        if created_date < age_limit:
            return False
            
        # Condition 4: Videos with spread rate within range
        spread_min = self.config.get('spread_rate_min', 3)
        spread_max = self.config.get('spread_rate_max', 8)
        high_diffusion_videos = []
        
        for video in videos:
            diffusion_rate = self.calculate_diffusion_rate(
                video['viewCount'], 
                channel_data['subscriberCount']
            )
            if spread_min <= diffusion_rate <= spread_max:
                high_diffusion_videos.append(video)
                
        if len(high_diffusion_videos) < 3:
            return False
            
        # Condition 5: Low personal branding
        is_low_personal = self.check_personal_branding(channel_data, videos)
        if not is_low_personal:
            return False
            
        # Save filtered channel data
        channel_data['high_diffusion_videos'] = high_diffusion_videos[:3]
        channel_data['is_personal'] = channel_data['personal_branding_score'] >= 3
        
        return True
    
    def extract_and_analyze_keywords(self, channel_data: Dict, videos: List[Dict]):
        """Extract keywords from video titles and analyze them"""
        if not videos:
            return
        
        # Extract keywords from video titles
        video_titles = [v['title'] for v in videos[:20]]  # Top 20 videos
        keywords = self.keyword_extractor.extract_keywords_from_titles(video_titles)
        
        # Expand keywords with autosuggest
        expanded_keywords = []
        for keyword in keywords[:10]:  # Limit to avoid quota issues
            suggestions = self.keyword_extractor.expand_with_autosuggest(
                keyword, 
                self.region, 
                self.config.get('language', 'en')
            )
            expanded_keywords.extend(suggestions)
        
        # Get unique keywords
        all_keywords = list(set(keywords + expanded_keywords))[:30]
        
        # Get metrics for keywords
        keyword_metrics = self.keyword_api.get_bulk_metrics(
            all_keywords,
            self.region,
            self.config.get('language', 'en')
        )
        
        # Store high-scoring keywords
        for metric in keyword_metrics:
            if metric['score'] >= 6:  # Only keep high-scoring keywords
                self.keyword_metrics.append(metric)
        
        # Add top keywords to channel data
        channel_data['top_keywords'] = [m['keyword'] for m in sorted(
            keyword_metrics, 
            key=lambda x: x['score'], 
            reverse=True
        )[:5]]
    
    def process_keyword(self, keyword: str):
        """Process each keyword"""
        print(f"Searching with keyword '{keyword}'...")
        channel_ids = self.search_channels_by_keyword(keyword)
        
        for channel_id in channel_ids:
            channel_data = self.get_channel_details(channel_id)
            if not channel_data:
                continue
                
            videos = self.get_channel_videos(channel_data['uploads_playlist_id'])
            
            if self.filter_channel(channel_data, videos):
                channel_data['search_keyword'] = keyword
                
                # Extract and analyze keywords for overseas markets
                if self.region != 'JP':
                    self.extract_and_analyze_keywords(channel_data, videos)
                
                self.channels_data.append(channel_data)
                print(f"  ✓ {channel_data['title']} matches criteria")
    
    def get_filtered_channels(self) -> List[Dict]:
        """Return filtered channel data"""
        return self.channels_data