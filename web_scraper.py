import time
import random
import re
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from langdetect import detect, LangDetectException

from config import Config

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """Web scraper for YouTube channels using Selenium"""
    
    def __init__(self):
        self.config = Config.get_region_config()
        self.scraper_config = Config.get_scraper_config()
        self.driver = None
        self.ua = UserAgent()
        
    def _get_driver(self, max_retries: int = 3):
        """Initialize Chrome driver with anti-detection measures and retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                options = webdriver.ChromeOptions()
                
                if self.scraper_config['headless']:
                    options.add_argument('--headless')
                    
                # Anti-detection arguments
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-gpu')
                options.add_argument(f'--window-size=1920,1080')
                
                # Random user agent
                if self.scraper_config['user_agent_rotation']:
                    user_agent = self.ua.random
                    options.add_argument(f'user-agent={user_agent}')
                    
                # Accept-Language header for US English
                # Commented out due to undetected-chromedriver v3 compatibility issue
                # options.add_experimental_option('prefs', {'intl.accept_languages': 'en-US,en'})
                
                driver = None
                
                if self.scraper_config['use_undetected_driver']:
                    # Try to use Chrome with explicit version if available
                    try:
                        chrome_version = self.scraper_config.get('chrome_version')
                        if chrome_version:
                            driver = uc.Chrome(options=options, version_main=int(chrome_version), use_subprocess=True)
                        else:
                            driver = uc.Chrome(options=options, use_subprocess=True)
                    except Exception as e:
                        logger.warning(f"Failed to initialize undetected Chrome driver: {e}")
                        # Fallback to regular Chrome driver
                        driver = webdriver.Chrome(options=options)
                else:
                    driver = webdriver.Chrome(options=options)
                    
                # Execute script to remove webdriver property
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Test the driver with a simple command
                driver.execute_script("return 1")
                
                logger.info(f"Successfully initialized Chrome driver on attempt {attempt + 1}")
                return driver
                
            except Exception as e:
                last_error = e
                logger.warning(f"Failed to initialize Chrome driver (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Clean up any failed driver instance
                if 'driver' in locals() and driver:
                    try:
                        driver.quit()
                    except:
                        pass
                        
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))  # Progressive delay
                    
        raise Exception(f"Failed to initialize Chrome driver after {max_retries} attempts: {str(last_error)}")
    
    def _random_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay to avoid detection"""
        time.sleep(random.uniform(min_seconds, max_seconds))
        
    def _scroll_page(self, scrolls: int = 5):
        """Scroll page to load more content"""
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            self._random_delay(1, 2)
            
    def _is_english_content(self, text: str) -> bool:
        """Check if content is in English"""
        if not text or len(text.strip()) < 10:
            return True  # Too short to detect reliably
            
        try:
            lang = detect(text)
            return lang == 'en'
        except LangDetectException:
            # If detection fails, check for English characters
            english_chars = sum(1 for c in text if ord(c) < 128)
            return english_chars / len(text) > 0.8
            
    def _parse_subscriber_count(self, text: str) -> int:
        """Parse subscriber count from text like '1.2M subscribers'"""
        if not text:
            return 0
            
        # Clean the text
        text = text.lower().replace('subscribers', '').replace('subscriber', '').strip()
        
        # Extract number
        match = re.search(r'([\d.]+)\s*([kmb])?', text)
        if not match:
            return 0
            
        number = float(match.group(1))
        multiplier = match.group(2)
        
        if multiplier == 'k':
            return int(number * 1000)
        elif multiplier == 'm':
            return int(number * 1_000_000)
        elif multiplier == 'b':
            return int(number * 1_000_000_000)
        
        return int(number)
        
    def _parse_view_count(self, text: str) -> int:
        """Parse view count from text like '1.2M views'"""
        if not text:
            return 0
            
        # Clean the text
        text = text.lower().replace('views', '').replace('view', '').strip()
        
        # Extract number
        match = re.search(r'([\d.]+)\s*([kmb])?', text)
        if not match:
            return 0
            
        number = float(match.group(1))
        multiplier = match.group(2)
        
        if multiplier == 'k':
            return int(number * 1000)
        elif multiplier == 'm':
            return int(number * 1_000_000)
        elif multiplier == 'b':
            return int(number * 1_000_000_000)
        
        return int(number)
        
    def search_channels(self, keywords: List[str], max_results: int = 100) -> List[Dict[str, Any]]:
        """Search for channels based on keywords"""
        channels = []
        driver = None
        
        try:
            driver = self._get_driver()
            self.driver = driver
            
            for keyword in keywords:
                try:
                    # Search URL with US region and English language
                    search_url = f"https://www.youtube.com/results?search_query={keyword}+channel&sp=EgIQAg%253D%253D&gl=US&hl=en"
                    
                    logger.info(f"Searching for keyword: {keyword}")
                    
                    # Retry navigation if connection fails
                    nav_retries = 3
                    for nav_attempt in range(nav_retries):
                        try:
                            self.driver.get(search_url)
                            self._random_delay(2, 4)
                            break
                        except Exception as nav_e:
                            if nav_attempt < nav_retries - 1:
                                logger.warning(f"Navigation failed, retrying: {nav_e}")
                                time.sleep(2)
                                # Check if driver is still alive
                                try:
                                    self.driver.execute_script("return 1")
                                except:
                                    logger.warning("Driver connection lost, reinitializing...")
                                    if self.driver:
                                        try:
                                            self.driver.quit()
                                        except:
                                            pass
                                    self.driver = self._get_driver()
                            else:
                                raise nav_e
                    
                    # Scroll to load more results
                    self._scroll_page(scrolls=10)
                    
                    # Parse page content
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    
                    # Find channel elements
                    channel_elements = soup.find_all('ytd-channel-renderer')
                    
                    for element in channel_elements[:max_results]:
                        try:
                            channel_data = self._extract_channel_data(element)
                            if channel_data and self._filter_channel(channel_data):
                                channels.append(channel_data)
                                logger.info(f"Found channel: {channel_data['title']}")
                                
                                if len(channels) >= self.config['search_limit']:
                                    break
                                    
                        except Exception as e:
                            logger.error(f"Error extracting channel data: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.error(f"Error searching keyword {keyword}: {str(e)}")
                    continue
                    
                # Delay between searches
                self._random_delay(self.config['request_delay'], self.config['request_delay'] + 2)
                
        except Exception as e:
            logger.error(f"Error during channel search: {str(e)}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            self.driver = None
                
        return channels
        
    def _extract_channel_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract channel data from search result element"""
        try:
            # Channel title
            title_element = element.find('yt-formatted-string', {'id': 'text'})
            title = title_element.text if title_element else ''
            
            # Channel URL
            link_element = element.find('a', {'id': 'main-link'})
            channel_url = f"https://www.youtube.com{link_element['href']}" if link_element else ''
            channel_id = link_element['href'].split('/')[-1] if link_element else ''
            
            # Subscriber count
            subscriber_element = element.find('yt-formatted-string', {'id': 'subscribers'})
            subscriber_text = subscriber_element.text if subscriber_element else '0'
            subscriber_count = self._parse_subscriber_count(subscriber_text)
            
            # Description
            description_element = element.find('yt-formatted-string', {'id': 'description'})
            description = description_element.text if description_element else ''
            
            # Check if content is in English
            combined_text = f"{title} {description}"
            if not self._is_english_content(combined_text):
                logger.info(f"Skipping non-English channel: {title}")
                return None
                
            return {
                'channelId': channel_id,
                'title': title,
                'description': description,
                'subscriberCount': subscriber_count,
                'url': channel_url,
                'language': 'en',
                'country': 'US'
            }
            
        except Exception as e:
            logger.error(f"Error parsing channel element: {str(e)}")
            return None
            
    def get_channel_details(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a channel"""
        try:
            if not self.driver:
                self.driver = self._get_driver()
                
            channel_url = f"https://www.youtube.com/channel/{channel_id}/about"
            self.driver.get(channel_url)
            self._random_delay(2, 4)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.scraper_config['timeout']).until(
                EC.presence_of_element_located((By.TAG_NAME, 'ytd-channel-about-metadata-renderer'))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract channel data
            channel_data = {
                'channelId': channel_id,
                'publishedAt': None,
                'videoCount': 0,
                'viewCount': 0
            }
            
            # Get join date
            stats_elements = soup.find_all('yt-formatted-string', {'class': 'style-scope ytd-channel-about-metadata-renderer'})
            for stat in stats_elements:
                text = stat.text
                if 'Joined' in text:
                    date_match = re.search(r'Joined (.+)', text)
                    if date_match:
                        try:
                            # Parse date
                            date_str = date_match.group(1)
                            channel_data['publishedAt'] = date_str
                        except:
                            pass
                            
            # Get video count and total views from Videos tab
            videos_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            self.driver.get(videos_url)
            self._random_delay(2, 3)
            
            # Count videos and get view counts
            video_elements = soup.find_all('ytd-grid-video-renderer')
            channel_data['videoCount'] = len(video_elements)
            
            total_views = 0
            for video in video_elements[:30]:  # Check first 30 videos
                view_element = video.find('span', string=re.compile(r'views'))
                if view_element:
                    views = self._parse_view_count(view_element.text)
                    total_views += views
                    
            channel_data['viewCount'] = total_views
            
            return channel_data
            
        except Exception as e:
            logger.error(f"Error getting channel details for {channel_id}: {str(e)}")
            return None
            
    def get_channel_videos(self, channel_id: str, max_results: int = 30) -> List[Dict[str, Any]]:
        """Get recent videos from a channel"""
        videos = []
        
        try:
            if not self.driver:
                self.driver = self._get_driver()
                
            videos_url = f"https://www.youtube.com/channel/{channel_id}/videos"
            
            # Retry navigation if connection fails
            nav_retries = 3
            for nav_attempt in range(nav_retries):
                try:
                    self.driver.get(videos_url)
                    self._random_delay(2, 4)
                    break
                except Exception as nav_e:
                    if nav_attempt < nav_retries - 1:
                        logger.warning(f"Navigation to videos page failed, retrying: {nav_e}")
                        time.sleep(2)
                        # Check if driver is still alive
                        try:
                            self.driver.execute_script("return 1")
                        except:
                            logger.warning("Driver connection lost, reinitializing...")
                            if self.driver:
                                try:
                                    self.driver.quit()
                                except:
                                    pass
                            self.driver = self._get_driver()
                    else:
                        raise nav_e
            
            # Scroll to load more videos
            self._scroll_page(scrolls=3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            video_elements = soup.find_all('ytd-grid-video-renderer')[:max_results]
            
            for element in video_elements:
                try:
                    video_data = self._extract_video_data(element)
                    if video_data:
                        videos.append(video_data)
                except Exception as e:
                    logger.error(f"Error extracting video data: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting videos for channel {channel_id}: {str(e)}")
            
        return videos
        
    def _extract_video_data(self, element) -> Optional[Dict[str, Any]]:
        """Extract video data from video element"""
        try:
            # Video title
            title_element = element.find('yt-formatted-string', {'id': 'video-title'})
            title = title_element.text if title_element else ''
            
            # Video ID
            link_element = element.find('a', {'id': 'video-title-link'})
            video_id = link_element['href'].split('v=')[-1] if link_element else ''
            
            # View count
            metadata_element = element.find('span', string=re.compile(r'views'))
            view_count = self._parse_view_count(metadata_element.text) if metadata_element else 0
            
            # Published date
            date_element = element.find('span', string=re.compile(r'ago'))
            published_text = date_element.text if date_element else ''
            
            return {
                'videoId': video_id,
                'title': title,
                'viewCount': view_count,
                'publishedAt': published_text
            }
            
        except Exception as e:
            logger.error(f"Error parsing video element: {str(e)}")
            return None
            
    def _filter_channel(self, channel: Dict[str, Any]) -> bool:
        """Filter channel based on criteria"""
        # Check subscriber count
        sub_count = channel.get('subscriberCount', 0)
        if sub_count < self.config['min_subs'] or sub_count > self.config['max_subs']:
            return False
            
        # Check if English content
        combined_text = f"{channel.get('title', '')} {channel.get('description', '')}"
        if not self._is_english_content(combined_text):
            return False
            
        return True
        
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None