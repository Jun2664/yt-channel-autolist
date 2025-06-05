import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for region-specific settings"""
    
    SUPPORTED_REGIONS = ['JP', 'US', 'EN', 'ES', 'PT', 'BR']
    REGION_LANGUAGE_MAP = {
        'JP': 'ja',
        'US': 'en',
        'EN': 'en',
        'ES': 'es',
        'PT': 'pt',
        'BR': 'pt'
    }
    
    @staticmethod
    def get_region_config(region: str) -> Dict[str, Any]:
        """Get configuration for a specific region"""
        region = region.upper()
        
        # Map US/BR to EN/PT for config purposes
        config_region = 'EN' if region == 'US' else 'PT' if region == 'BR' else region
        
        if config_region not in ['JP', 'EN', 'ES', 'PT']:
            config_region = os.getenv('DEFAULT_REGION', 'JP')
        
        return {
            'min_volume': int(os.getenv(f'{config_region}_MIN_VOLUME', 500000)),
            'max_subs': int(os.getenv(f'{config_region}_MAX_SUBS', 20000)),
            'max_videos': int(os.getenv(f'{config_region}_MAX_VIDEOS', 30)),
            'spread_rate_min': float(os.getenv(f'{config_region}_SPREAD_RATE_MIN', 3)),
            'spread_rate_max': float(os.getenv(f'{config_region}_SPREAD_RATE_MAX', 8)),
            'channel_age_days': int(os.getenv(f'{config_region}_CHANNEL_AGE_DAYS', 60)),
            'language': Config.REGION_LANGUAGE_MAP.get(region, 'en')
        }
    
    @staticmethod
    def get_api_keys() -> Dict[str, str]:
        """Get API keys from environment"""
        return {
            'youtube': os.getenv('YOUTUBE_API_KEY', ''),
            'vidiq': os.getenv('VIDIQ_API_KEY', ''),
            'tubebuddy': os.getenv('TUBEBUDDY_API_KEY', ''),
            'keywordtool': os.getenv('KEYWORDTOOL_API_KEY', '')
        }
    
    @staticmethod
    def get_google_credentials() -> str:
        """Get Google service account JSON from environment"""
        return os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')