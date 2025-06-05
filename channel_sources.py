from typing import List, Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from datetime import datetime, timedelta

class ChannelSources:
    """Different sources for discovering YouTube channels"""
    
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_trending_channels(self, region_code: str = 'US', category_id: Optional[str] = None) -> List[str]:
        """Get channels from YouTube trending videos"""
        channel_ids = set()
        
        try:
            # Get trending videos
            request = self.youtube.videos().list(
                part='snippet',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=50,
                categoryId=category_id if category_id else None
            )
            
            response = request.execute()
            
            # Extract unique channel IDs
            for item in response.get('items', []):
                channel_id = item['snippet']['channelId']
                channel_ids.add(channel_id)
            
        except HttpError as e:
            print(f"Error fetching trending videos: {e}")
        
        return list(channel_ids)
    
    def get_channels_by_category(self, region_code: str = 'US', categories: List[str] = None) -> List[str]:
        """Get channels from specific categories"""
        if not categories:
            # Default categories for content creators
            categories = [
                '1',   # Film & Animation
                '2',   # Cars & Vehicles
                '10',  # Music
                '15',  # Pets & Animals
                '17',  # Sports
                '19',  # Travel & Events
                '20',  # Gaming
                '22',  # People & Blogs
                '23',  # Comedy
                '24',  # Entertainment
                '25',  # News & Politics
                '26',  # How-to & Style
                '27',  # Education
                '28',  # Science & Technology
            ]
        
        all_channel_ids = set()
        
        for category in categories:
            channel_ids = self.get_trending_channels(region_code, category)
            all_channel_ids.update(channel_ids)
        
        return list(all_channel_ids)
    
    def search_rising_channels(self, keywords: List[str], region_code: str = 'US', 
                             published_after: Optional[datetime] = None) -> List[str]:
        """Search for rising channels using keywords with date filter"""
        channel_ids = set()
        
        if not published_after:
            # Default to channels created in last 60 days
            published_after = datetime.now() - timedelta(days=60)
        
        for keyword in keywords:
            try:
                request = self.youtube.search().list(
                    part='snippet',
                    q=keyword,
                    type='channel',
                    regionCode=region_code,
                    publishedAfter=published_after.isoformat() + 'Z',
                    order='date',
                    maxResults=50
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    channel_id = item['id']['channelId']
                    channel_ids.add(channel_id)
                    
            except HttpError as e:
                print(f"Error searching for keyword '{keyword}': {e}")
        
        return list(channel_ids)
    
    def get_social_blade_trending(self, region: str = 'US', limit: int = 100) -> List[Dict[str, str]]:
        """
        Get trending creators from Social Blade (mock implementation)
        Note: Social Blade requires API key and paid subscription
        This is a placeholder for the actual implementation
        """
        # In a real implementation, this would call Social Blade API
        # For now, return empty list
        print(f"Social Blade integration not implemented. Using YouTube API for region: {region}")
        return []
    
    def get_recommended_channels(self, seed_channel_ids: List[str], region_code: str = 'US') -> List[str]:
        """Get recommended channels based on seed channels"""
        recommended_ids = set()
        
        for channel_id in seed_channel_ids[:5]:  # Limit to avoid quota issues
            try:
                # Get channel's featured channels
                request = self.youtube.channels().list(
                    part='brandingSettings',
                    id=channel_id
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    branding = item.get('brandingSettings', {})
                    channel = branding.get('channel', {})
                    
                    # Get featured channels
                    featured_channels = channel.get('featuredChannelsUrls', [])
                    for featured_url in featured_channels[:10]:
                        # Extract channel ID from URL
                        if '/channel/' in featured_url:
                            featured_id = featured_url.split('/channel/')[-1]
                            recommended_ids.add(featured_id)
                        elif '/c/' in featured_url or '/user/' in featured_url:
                            # Would need additional API call to resolve custom URLs
                            pass
                            
            except HttpError as e:
                print(f"Error getting recommendations for channel {channel_id}: {e}")
        
        return list(recommended_ids)