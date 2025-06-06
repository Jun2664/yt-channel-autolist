import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from web_scraper import YouTubeScraper as WebScraper
from channel_sources import ChannelSources
from keyword_extractor import KeywordExtractor
from keyword_research_api import KeywordResearchAPI
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """Main YouTube scraper that uses web scraping instead of API"""
    
    def __init__(self, api_key: str = None, region: str = 'US', config: Dict = None, api_keys: Dict = None):
        """Initialize scraper (api_key parameter kept for compatibility but not used)"""
        self.region = 'US'  # Fixed to US
        self.config = config or {}
        self.channels_data = []
        self.keyword_metrics = []
        
        # Initialize web scraper
        self.web_scraper = WebScraper()
        
        # Initialize helper modules
        self.keyword_extractor = KeywordExtractor(self.config.get('language', 'en'))
        
        # Initialize keyword research API (still useful for keyword expansion)
        if api_keys:
            self.keyword_api = KeywordResearchAPI(
                vidiq_key=api_keys.get('vidiq', ''),
                tubebuddy_key=api_keys.get('tubebuddy', ''),
                keywordtool_key=api_keys.get('keywordtool', '')
            )
        else:
            self.keyword_api = KeywordResearchAPI()
    
    def search_channels_by_keyword(self, keyword: str, max_results: int = 50) -> List[str]:
        """Search channels by keyword using web scraping"""
        try:
            # Use web scraper to search channels
            channels = self.web_scraper.search_channels([keyword], max_results)
            channel_ids = [channel['channelId'] for channel in channels]
            
            # Store channel data for later use
            for channel in channels:
                self.channels_data.append(channel)
            
            return channel_ids
            
        except Exception as e:
            logger.error(f"Error searching channels for keyword '{keyword}': {str(e)}")
            return []
    
    def get_channel_details(self, channel_id: str) -> Optional[Dict]:
        """Get channel details using web scraping"""
        try:
            # Check if we already have this channel's data from search
            for channel in self.channels_data:
                if channel.get('channelId') == channel_id:
                    # Get additional details from channel page
                    details = self.web_scraper.get_channel_details(channel_id)
                    if details:
                        channel.update(details)
                    
                    return {
                        'id': channel_id,
                        'title': channel.get('title', ''),
                        'description': channel.get('description', ''),
                        'publishedAt': details.get('publishedAt') if details else None,
                        'thumbnails': {},  # Not available via scraping
                        'subscriberCount': channel.get('subscriberCount', 0),
                        'videoCount': details.get('videoCount', 0) if details else 0,
                        'viewCount': details.get('viewCount', 0) if details else 0,
                        'uploads_playlist_id': None,  # Not used in scraping
                        'region': 'US',
                        'language': 'en'
                    }
            
            # If not found in cache, get details directly
            channel = self.web_scraper.get_channel_details(channel_id)
            if not channel:
                return None
            
            return {
                'id': channel_id,
                'title': '',  # Would need to scrape channel page for this
                'description': '',
                'publishedAt': channel.get('publishedAt'),
                'thumbnails': {},
                'subscriberCount': 0,  # Would need to scrape channel page
                'videoCount': channel.get('videoCount', 0),
                'viewCount': channel.get('viewCount', 0),
                'uploads_playlist_id': None,
                'region': 'US',
                'language': 'en'
            }
            
        except Exception as e:
            logger.error(f"Error getting channel details for ID {channel_id}: {str(e)}")
            return None
    
    def get_channel_videos(self, channel_id: str, max_results: int = 30) -> List[Dict]:
        """Get channel videos using web scraping"""
        try:
            videos = self.web_scraper.get_channel_videos(channel_id, max_results)
            
            # Format videos to match expected structure
            formatted_videos = []
            for video in videos:
                formatted_videos.append({
                    'id': video.get('videoId', ''),
                    'title': video.get('title', ''),
                    'publishedAt': video.get('publishedAt', ''),
                    'viewCount': video.get('viewCount', 0),
                    'likeCount': 0,  # Not available via scraping
                    'commentCount': 0,  # Not available via scraping
                    'thumbnails': {}  # Not included in scraping
                })
            
            return formatted_videos
            
        except Exception as e:
            logger.error(f"Error getting videos for channel {channel_id}: {str(e)}")
            return []
    
    def calculate_diffusion_rate(self, view_count: int, subscriber_count: int) -> float:
        """Calculate diffusion rate"""
        if subscriber_count == 0:
            return 0
        return view_count / subscriber_count
    
    def check_personal_branding(self, channel_data: Dict, videos: List[Dict]) -> bool:
        """Check personal branding - Returns True if low personal branding (business-suitable)"""
        reasons = []
        score = 0
        
        # Personal keywords for English content
        personal_keywords = [
            'face', 'selfie', 'man', 'woman', 'boy', 'girl', 'host', 'actor', 
            'vlog', 'vlogger', 'interview', 'my', 'me', 'personal', 'daily', 
            'routine', 'life', 'grwm', 'day in my life', 'morning routine',
            'night routine', 'lifestyle', 'diary', 'journal'
        ]
        
        channel_title = channel_data.get('title', '').lower()
        channel_description = channel_data.get('description', '').lower()
        
        # Check channel name patterns
        personal_patterns = ['vlog', 'life', 'diary', 'personal', 'lifestyle', 'daily']
        
        if any(pattern in channel_title for pattern in personal_patterns):
            score += 3
            reasons.append("Personal pattern in channel name")
        
        # Check channel name and description
        channel_text = f"{channel_title} {channel_description}"
        
        # Personal keyword check
        found_keywords = []
        for keyword in personal_keywords:
            if keyword in channel_text:
                score += 2
                found_keywords.append(keyword)
        
        if found_keywords:
            reasons.append(f"Keywords detected: {', '.join(found_keywords[:3])}")
        
        # Check first person pronouns in description
        first_person_keywords = ['i', 'me', 'my', 'myself', "i'm", "i've", "i'll"]
        first_person_count = sum(1 for word in first_person_keywords if word in channel_description)
        
        if first_person_count >= 3:
            score += 3
            reasons.append("Frequent first person usage")
        elif first_person_count >= 1:
            score += 1
            reasons.append("Contains first person")
        
        # Check video titles
        video_titles = ' '.join([video.get('title', '').lower() for video in videos[:10]])
        video_keywords_found = []
        for keyword in personal_keywords:
            if keyword in video_titles:
                score += 1
                video_keywords_found.append(keyword)
        
        if video_keywords_found:
            reasons.append(f"In video titles: {', '.join(set(video_keywords_found[:3]))}")
        
        # Check for vlog-style content
        vlog_indicators = ['vlog', 'day in', 'routine', 'grwm', 'lifestyle', 'diary']
        videos_with_vlogs = sum(1 for v in videos[:10] 
                              if any(kw in v.get('title', '').lower() for kw in vlog_indicators))
        
        if videos_with_vlogs >= 8:  # 80% or more
            score += 3
            reasons.append("Mostly vlog-style content")
        elif videos_with_vlogs >= 5:  # 50% or more
            score += 1
            reasons.append("Half or more vlog-style content")
        
        # Save judgment reasons
        channel_data['personal_branding_score'] = min(score, 10)
        channel_data['personal_branding_reasons'] = ' + '.join(reasons) if reasons else "No personal branding"
        
        # Score of 3 or higher indicates high personal branding (return False = not suitable)
        return score < 3
    
    def filter_channels(self, channels: List[Dict]) -> List[Dict]:
        """Filter channels based on criteria"""
        filtered = []
        
        for channel in channels:
            try:
                # Basic criteria check
                subs = channel.get('subscriberCount', 0)
                videos = channel.get('videoCount', 0)
                
                # Check subscriber count
                if subs < self.config.get('min_subs', 100):
                    logger.info(f"Skipping {channel.get('title')}: Too few subscribers ({subs})")
                    continue
                    
                if subs > self.config.get('max_subs', 50000):
                    logger.info(f"Skipping {channel.get('title')}: Too many subscribers ({subs})")
                    continue
                
                # Check video count
                if videos > self.config.get('max_videos', 30):
                    logger.info(f"Skipping {channel.get('title')}: Too many videos ({videos})")
                    continue
                
                # Check language (English only)
                title = channel.get('title', '')
                description = channel.get('description', '')
                combined_text = f"{title} {description}"
                
                if combined_text.strip():
                    try:
                        lang = detect(combined_text)
                        if lang != 'en':
                            logger.info(f"Skipping {title}: Non-English content detected ({lang})")
                            continue
                    except LangDetectException:
                        # If detection fails, check for English characters
                        english_chars = sum(1 for c in combined_text if ord(c) < 128)
                        if english_chars / len(combined_text) < 0.8:
                            logger.info(f"Skipping {title}: Low English character ratio")
                            continue
                
                # Check diffusion rate if we have view data
                if 'viewCount' in channel and subs > 0:
                    diffusion_rate = self.calculate_diffusion_rate(channel['viewCount'], subs)
                    
                    if diffusion_rate < self.config.get('spread_rate_min', 2):
                        logger.info(f"Skipping {title}: Low diffusion rate ({diffusion_rate:.1f})")
                        continue
                        
                    if diffusion_rate > self.config.get('spread_rate_max', 6):
                        logger.info(f"Skipping {title}: High diffusion rate ({diffusion_rate:.1f})")
                        continue
                    
                    channel['diffusion_rate'] = diffusion_rate
                
                filtered.append(channel)
                
            except Exception as e:
                logger.error(f"Error filtering channel: {str(e)}")
                continue
        
        return filtered
    
    def analyze_channels(self, keywords: List[str]) -> List[Dict]:
        """Analyze channels based on keywords"""
        all_channels = []
        
        try:
            # Search for channels
            channels = self.web_scraper.search_channels(keywords, self.config.get('search_limit', 1000))
            
            # Filter channels
            filtered_channels = self.filter_channels(channels)
            
            # Get additional details and videos for each channel
            for channel in filtered_channels:
                channel_id = channel.get('channelId')
                
                # Get channel videos
                videos = self.get_channel_videos(channel_id)
                
                # Check personal branding
                is_business_suitable = self.check_personal_branding(channel, videos)
                
                if not is_business_suitable:
                    logger.info(f"Skipping {channel.get('title')}: High personal branding score")
                    continue
                
                # Extract keywords from videos
                if videos:
                    video_titles = [v.get('title', '') for v in videos]
                    extracted_keywords = self.keyword_extractor.extract_keywords(video_titles)
                    channel['extracted_keywords'] = extracted_keywords
                    
                    # Get keyword metrics
                    if extracted_keywords:
                        keyword_data = self.keyword_api.get_keyword_data(extracted_keywords[:5])
                        channel['keyword_metrics'] = keyword_data
                
                all_channels.append(channel)
                
                logger.info(f"Added channel: {channel.get('title')} ({len(all_channels)} total)")
                
                # Check if we have enough channels
                if len(all_channels) >= 300:
                    logger.info("Reached 300 channels, stopping search")
                    break
                    
        except Exception as e:
            logger.error(f"Error analyzing channels: {str(e)}")
        finally:
            # Close the web scraper
            self.web_scraper.close()
        
        return all_channels
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'web_scraper'):
            self.web_scraper.close()