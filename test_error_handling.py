import unittest
from unittest.mock import Mock, patch, MagicMock
from googleapiclient.errors import HttpError
from youtube_scraper import YouTubeScraper
from sheets_writer import SheetsWriter
import json


class TestErrorHandling(unittest.TestCase):
    """Test error handling for YouTube API and Google Drive API"""
    
    def setUp(self):
        self.youtube_scraper = YouTubeScraper(api_key='test_api_key', region='JP')
        
    def test_channel_404_error_handling(self):
        """Test handling of 404 error when channel not found"""
        # Mock 404 response
        resp = Mock()
        resp.status = 404
        content = json.dumps({
            'error': {
                'errors': [{
                    'reason': 'channelNotFound',
                    'message': 'The channel identified with the request\'s <code>channelId</code> parameter cannot be found.'
                }]
            }
        }).encode('utf-8')
        
        error = HttpError(resp=resp, content=content)
        
        with patch.object(self.youtube_scraper.youtube.channels(), 'list') as mock_list:
            mock_list.return_value.execute.side_effect = error
            
            result = self.youtube_scraper.get_channel_details('UC_invalid_channel')
            self.assertIsNone(result)
    
    def test_playlist_404_error_handling(self):
        """Test handling of 404 error when playlist not found"""
        # Mock 404 response for playlist not found
        resp = Mock()
        resp.status = 404
        content = json.dumps({
            'error': {
                'errors': [{
                    'reason': 'playlistNotFound',
                    'message': 'The playlist identified with the request\'s <code>playlistId</code> parameter cannot be found.'
                }]
            }
        }).encode('utf-8')
        
        error = HttpError(resp=resp, content=content)
        
        with patch.object(self.youtube_scraper.youtube.playlistItems(), 'list') as mock_list:
            mock_list.return_value.execute.side_effect = error
            
            # Should return empty list instead of raising error
            result = self.youtube_scraper.get_channel_videos('UU_invalid_playlist')
            self.assertEqual(result, [])
    
    def test_channel_response_without_items(self):
        """Test handling of API response without 'items' key"""
        # Mock response without 'items' key
        mock_response = {}
        
        with patch.object(self.youtube_scraper.youtube.channels(), 'list') as mock_list:
            mock_list.return_value.execute.return_value = mock_response
            
            result = self.youtube_scraper.get_channel_details('UC_test_channel')
            self.assertIsNone(result)
    
    def test_playlist_response_without_items(self):
        """Test handling of playlist API response without 'items' key"""
        # Mock response without 'items' key
        mock_response = {}
        
        with patch.object(self.youtube_scraper.youtube.playlistItems(), 'list') as mock_list:
            mock_list.return_value.execute.return_value = mock_response
            
            # Should handle gracefully and check videos API
            with patch.object(self.youtube_scraper.youtube.videos(), 'list') as mock_videos:
                mock_videos.return_value.execute.return_value = {'items': []}
                
                result = self.youtube_scraper.get_channel_videos('UU_test_playlist')
                self.assertEqual(result, [])
    
    @patch('gspread.authorize')
    def test_google_drive_api_disabled_error(self, mock_authorize):
        """Test handling of Google Drive API disabled error"""
        # Mock SERVICE_DISABLED error
        mock_client = MagicMock()
        mock_authorize.return_value = mock_client
        
        # Mock error when creating spreadsheet
        mock_client.open.side_effect = Exception("SpreadsheetNotFound")
        mock_client.create.side_effect = Exception(
            "HttpError 403: Google Drive API has not been used in project 366095154373 before or it is disabled"
        )
        
        service_account_json = '{"type": "service_account", "project_id": "test"}'
        
        try:
            writer = SheetsWriter(service_account_json)
            writer.create_or_get_spreadsheet("Test Spreadsheet")
            self.fail("Expected exception was not raised")
        except Exception as e:
            self.assertIn("Google Drive API is not enabled", str(e))
            self.assertIn("https://console.cloud.google.com/apis/library/drive.googleapis.com", str(e))
    
    def test_general_http_error_handling(self):
        """Test handling of general HTTP errors"""
        # Mock 500 server error
        resp = Mock()
        resp.status = 500
        content = json.dumps({
            'error': {
                'errors': [{
                    'reason': 'backendError',
                    'message': 'Backend Error'
                }]
            }
        }).encode('utf-8')
        
        error = HttpError(resp=resp, content=content)
        
        with patch.object(self.youtube_scraper.youtube.channels(), 'list') as mock_list:
            mock_list.return_value.execute.side_effect = error
            
            result = self.youtube_scraper.get_channel_details('UC_test_channel')
            self.assertIsNone(result)
    
    def test_search_error_handling(self):
        """Test error handling in search_channels_by_keyword"""
        # Mock API error
        resp = Mock()
        resp.status = 403
        content = json.dumps({
            'error': {
                'errors': [{
                    'reason': 'quotaExceeded',
                    'message': 'Quota exceeded'
                }]
            }
        }).encode('utf-8')
        
        error = HttpError(resp=resp, content=content)
        
        with patch.object(self.youtube_scraper.youtube.search(), 'list') as mock_list:
            mock_list.return_value.execute.side_effect = error
            
            result = self.youtube_scraper.search_channels_by_keyword('test keyword')
            self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()