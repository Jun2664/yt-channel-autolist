#!/usr/bin/env python3
"""
Test script for overseas keyword selection features
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from config import Config
from keyword_extractor import KeywordExtractor
from keyword_research_api import KeywordResearchAPI
from channel_sources import ChannelSources

class TestOverseasFeatures(unittest.TestCase):
    
    def test_config_region_settings(self):
        """Test region-specific configuration"""
        # Test English market config
        en_config = Config.get_region_config('EN')
        self.assertEqual(en_config['max_subs'], 50000)
        self.assertEqual(en_config['spread_rate_min'], 2)
        self.assertEqual(en_config['spread_rate_max'], 6)
        self.assertEqual(en_config['language'], 'en')
        
        # Test Japanese market config
        jp_config = Config.get_region_config('JP')
        self.assertEqual(jp_config['max_subs'], 20000)
        self.assertEqual(jp_config['spread_rate_min'], 3)
        self.assertEqual(jp_config['spread_rate_max'], 8)
        self.assertEqual(jp_config['language'], 'ja')
        
        # Test US maps to EN config
        us_config = Config.get_region_config('US')
        self.assertEqual(us_config['language'], 'en')
    
    def test_keyword_extraction(self):
        """Test keyword extraction from video titles"""
        extractor = KeywordExtractor('en')
        
        titles = [
            "How to Build a Gaming PC - Complete Guide 2024",
            "Best Gaming PC Build Under $1000",
            "Gaming PC Setup Tour - RGB Everything!"
        ]
        
        keywords = extractor.extract_keywords_from_titles(titles)
        
        # Should extract gaming-related keywords
        self.assertTrue(any('gaming pc' in kw.lower() for kw in keywords))
        self.assertTrue(len(keywords) > 0)
    
    def test_ngram_extraction(self):
        """Test n-gram extraction"""
        extractor = KeywordExtractor('en')
        
        text = "How to build a gaming PC step by step"
        bigrams = extractor.extract_ngrams(text, 2)
        
        # Should contain relevant bigrams
        self.assertTrue(any('gaming pc' in bg for bg in bigrams))
        self.assertTrue(any('build gaming' in bg for bg in bigrams))
    
    @patch('requests.get')
    def test_youtube_autosuggest(self, mock_get):
        """Test YouTube autosuggest expansion"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            "gaming pc",
            [
                "gaming pc build",
                "gaming pc setup",
                "gaming pc under 1000",
                "gaming pc vs console",
                "gaming pc build guide"
            ]
        ]
        mock_get.return_value = mock_response
        
        extractor = KeywordExtractor('en')
        suggestions = extractor.expand_with_autosuggest('gaming pc', 'US', 'en')
        
        self.assertTrue(len(suggestions) > 0)
        self.assertTrue(any('build' in s for s in suggestions))
    
    def test_keyword_scoring(self):
        """Test keyword scoring calculation"""
        api = KeywordResearchAPI()
        
        # Test scoring logic
        score1 = api._get_mock_metrics('gaming pc', 'US', 'en')
        score2 = api._get_mock_metrics('how to build gaming pc setup guide', 'US', 'en')
        
        # Shorter keywords should generally have higher volume but also higher competition
        self.assertIsInstance(score1['search_volume'], int)
        self.assertIsInstance(score1['competition'], float)
        self.assertIsInstance(score1['score'], float)
        
        # Longer keywords should have lower competition
        self.assertTrue(score2['competition'] < score1['competition'])
    
    @patch('googleapiclient.discovery.build')
    def test_channel_sources_trending(self, mock_build):
        """Test getting trending channels"""
        # Mock YouTube API
        mock_youtube = Mock()
        mock_videos = Mock()
        mock_youtube.videos.return_value = mock_videos
        
        mock_videos.list.return_value.execute.return_value = {
            'items': [
                {'snippet': {'channelId': 'UC123'}},
                {'snippet': {'channelId': 'UC456'}},
                {'snippet': {'channelId': 'UC789'}},
            ]
        }
        
        mock_build.return_value = mock_youtube
        
        sources = ChannelSources('fake-api-key')
        channel_ids = sources.get_trending_channels('US')
        
        self.assertEqual(len(channel_ids), 3)
        self.assertIn('UC123', channel_ids)
    
    def test_region_language_mapping(self):
        """Test region to language mapping"""
        self.assertEqual(Config.REGION_LANGUAGE_MAP['US'], 'en')
        self.assertEqual(Config.REGION_LANGUAGE_MAP['BR'], 'pt')
        self.assertEqual(Config.REGION_LANGUAGE_MAP['ES'], 'es')
        self.assertEqual(Config.REGION_LANGUAGE_MAP['JP'], 'ja')

if __name__ == '__main__':
    unittest.main()