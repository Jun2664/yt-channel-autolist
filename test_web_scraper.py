import unittest
from unittest.mock import Mock, patch, MagicMock
from web_scraper import YouTubeScraper as WebScraper
from youtube_scraper import YouTubeScraper
import logging


class TestWebScraper(unittest.TestCase):
    """Test web scraper functionality"""
    
    def setUp(self):
        # Set up logging to suppress messages during tests
        logging.disable(logging.CRITICAL)
        
    def tearDown(self):
        # Re-enable logging
        logging.disable(logging.NOTSET)
    
    @patch('web_scraper.uc.Chrome')
    @patch('web_scraper.webdriver.Chrome')
    def test_driver_initialization(self, mock_chrome, mock_uc_chrome):
        """Test Chrome driver initialization with anti-detection measures"""
        scraper = WebScraper()
        
        # Mock driver
        mock_driver = MagicMock()
        mock_uc_chrome.return_value = mock_driver
        
        driver = scraper._get_driver()
        
        # Check that undetected chrome was used
        mock_uc_chrome.assert_called_once()
        
        # Check that webdriver property was removed
        mock_driver.execute_script.assert_called_with(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    
    def test_parse_subscriber_count(self):
        """Test parsing subscriber count from various formats"""
        scraper = WebScraper()
        
        test_cases = [
            ('1.2K subscribers', 1200),
            ('500 subscribers', 500),
            ('2.5M subscribers', 2500000),
            ('1B subscribers', 1000000000),
            ('123', 123),
            ('', 0),
            ('no numbers here', 0),
        ]
        
        for text, expected in test_cases:
            result = scraper._parse_subscriber_count(text)
            self.assertEqual(result, expected, f"Failed for: {text}")
    
    def test_parse_view_count(self):
        """Test parsing view count from various formats"""
        scraper = WebScraper()
        
        test_cases = [
            ('1.2K views', 1200),
            ('500 views', 500),
            ('2.5M views', 2500000),
            ('', 0),
            ('no numbers', 0),
        ]
        
        for text, expected in test_cases:
            result = scraper._parse_view_count(text)
            self.assertEqual(result, expected, f"Failed for: {text}")
    
    def test_is_english_content(self):
        """Test English content detection"""
        scraper = WebScraper()
        
        # English content
        self.assertTrue(scraper._is_english_content("Hello, this is an English channel"))
        self.assertTrue(scraper._is_english_content("Tech Reviews and Tutorials"))
        
        # Non-English content
        self.assertFalse(scraper._is_english_content("こんにちは、日本語のチャンネルです"))
        self.assertFalse(scraper._is_english_content("Hola, este es un canal en español"))
        
        # Mixed content (should be false if mostly non-English)
        self.assertFalse(scraper._is_english_content("日本語チャンネル English"))
        
        # Too short to detect
        self.assertTrue(scraper._is_english_content("Hi"))
        self.assertTrue(scraper._is_english_content(""))
    
    def test_filter_channel(self):
        """Test channel filtering logic"""
        scraper = WebScraper()
        scraper.config = {
            'min_subs': 100,
            'max_subs': 50000
        }
        
        # Valid channel
        valid_channel = {
            'channelId': 'test123',
            'title': 'Tech Reviews',
            'description': 'We review the latest tech products',
            'subscriberCount': 5000,
            'language': 'en'
        }
        self.assertTrue(scraper._filter_channel(valid_channel))
        
        # Too few subscribers
        low_subs = valid_channel.copy()
        low_subs['subscriberCount'] = 50
        self.assertFalse(scraper._filter_channel(low_subs))
        
        # Too many subscribers
        high_subs = valid_channel.copy()
        high_subs['subscriberCount'] = 100000
        self.assertFalse(scraper._filter_channel(high_subs))
        
        # Non-English content
        non_english = valid_channel.copy()
        non_english['title'] = '日本語チャンネル'
        non_english['description'] = '日本語の説明'
        self.assertFalse(scraper._filter_channel(non_english))
    
    def test_extract_channel_data(self):
        """Test channel data extraction from HTML element"""
        scraper = WebScraper()
        
        # Mock BeautifulSoup element
        mock_element = MagicMock()
        
        # Mock title element
        mock_title = MagicMock()
        mock_title.text = "Tech Channel"
        mock_element.find.side_effect = [
            mock_title,  # title
            {'href': '/channel/UC123'},  # link
            MagicMock(text='10K subscribers'),  # subscribers
            MagicMock(text='Reviews of tech products')  # description
        ]
        
        result = scraper._extract_channel_data(mock_element)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Tech Channel')
        self.assertEqual(result['channelId'], 'UC123')
        self.assertEqual(result['subscriberCount'], 10000)
        self.assertEqual(result['language'], 'en')
        self.assertEqual(result['country'], 'US')
    
    def test_youtube_scraper_integration(self):
        """Test integration with main YouTubeScraper class"""
        config = {
            'min_subs': 100,
            'max_subs': 50000,
            'language': 'en',
            'search_limit': 100
        }
        
        scraper = YouTubeScraper(api_key=None, region='US', config=config)
        
        # Verify web scraper was initialized
        self.assertIsNotNone(scraper.web_scraper)
        self.assertEqual(scraper.region, 'US')
        self.assertEqual(scraper.config['language'], 'en')
    
    def test_personal_branding_check(self):
        """Test personal branding detection"""
        scraper = YouTubeScraper(api_key=None, region='US')
        
        # Business channel (low personal branding)
        business_channel = {
            'title': 'Tech Reviews Hub',
            'description': 'We provide in-depth reviews of the latest technology'
        }
        business_videos = [
            {'title': 'iPhone 15 Review'},
            {'title': 'Best Laptops 2024'},
            {'title': 'Gaming Monitor Comparison'}
        ]
        
        self.assertTrue(scraper.check_personal_branding(business_channel, business_videos))
        
        # Personal vlog channel (high personal branding)
        personal_channel = {
            'title': "Sarah's Lifestyle Vlog",
            'description': "Hi! I'm Sarah and I share my daily life adventures"
        }
        personal_videos = [
            {'title': 'My Morning Routine'},
            {'title': 'Day in My Life as a Student'},
            {'title': 'GRWM for Date Night'}
        ]
        
        self.assertFalse(scraper.check_personal_branding(personal_channel, personal_videos))
    
    def test_filter_channels(self):
        """Test channel filtering in main scraper"""
        config = {
            'min_subs': 100,
            'max_subs': 50000,
            'max_videos': 30,
            'spread_rate_min': 2,
            'spread_rate_max': 6
        }
        
        scraper = YouTubeScraper(api_key=None, region='US', config=config)
        
        channels = [
            {
                'title': 'Valid Channel',
                'description': 'Tech reviews and tutorials',
                'subscriberCount': 5000,
                'videoCount': 20,
                'viewCount': 15000
            },
            {
                'title': 'Too Few Subs',
                'description': 'New channel',
                'subscriberCount': 50,
                'videoCount': 5
            },
            {
                'title': 'Non-English',
                'description': '日本語のチャンネル',
                'subscriberCount': 1000,
                'videoCount': 10
            }
        ]
        
        filtered = scraper.filter_channels(channels)
        
        # Should only include the valid channel
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['title'], 'Valid Channel')
        self.assertIn('diffusion_rate', filtered[0])


if __name__ == '__main__':
    unittest.main()