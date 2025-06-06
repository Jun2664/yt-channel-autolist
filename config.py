import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for US/English-only web scraping"""
    
    # Fixed to US/English only
    SUPPORTED_REGIONS = ['US']
    REGION_LANGUAGE_MAP = {
        'US': 'en'
    }
    
    # Country code for YouTube search
    COUNTRY_CODE = 'US'
    
    # Language code for content filtering
    LANGUAGE = 'en'
    
    @staticmethod
    def get_region_config(region: str = 'US') -> Dict[str, Any]:
        """Get configuration for US region only"""
        return {
            'min_volume': int(os.getenv('US_MIN_VOLUME', 500000)),
            'max_subs': int(os.getenv('US_MAX_SUBS', 50000)),
            'min_subs': int(os.getenv('US_MIN_SUBS', 100)),  # New: minimum subscriber count
            'max_videos': int(os.getenv('US_MAX_VIDEOS', 30)),
            'spread_rate_min': float(os.getenv('US_SPREAD_RATE_MIN', 2)),
            'spread_rate_max': float(os.getenv('US_SPREAD_RATE_MAX', 6)),
            'channel_age_days': int(os.getenv('US_CHANNEL_AGE_DAYS', 60)),
            'language': 'en',
            'country_code': 'US',
            'search_limit': int(os.getenv('SEARCH_LIMIT', 1000)),  # Max channels to analyze per search
            'request_delay': float(os.getenv('REQUEST_DELAY', 2))  # Delay between requests in seconds
        }
    
    @staticmethod
    def get_api_keys() -> Dict[str, str]:
        """Get API keys from environment (for keyword research only)"""
        return {
            'vidiq': os.getenv('VIDIQ_API_KEY', ''),
            'tubebuddy': os.getenv('TUBEBUDDY_API_KEY', ''),
            'keywordtool': os.getenv('KEYWORDTOOL_API_KEY', '')
        }
    
    @staticmethod
    def get_google_credentials() -> str:
        """Get Google service account JSON from environment"""
        return os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')
    
    @staticmethod
    def get_scraper_config() -> Dict[str, Any]:
        """Get configuration for web scraper"""
        return {
            'use_undetected_driver': bool(os.getenv('USE_UNDETECTED_DRIVER', 'true').lower() == 'true'),
            'headless': bool(os.getenv('SCRAPER_HEADLESS', 'true').lower() == 'true'),
            'user_agent_rotation': bool(os.getenv('USER_AGENT_ROTATION', 'true').lower() == 'true'),
            'max_retries': int(os.getenv('MAX_RETRIES', 3)),
            'timeout': int(os.getenv('PAGE_TIMEOUT', 30))
        }