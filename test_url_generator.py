import unittest
from unittest.mock import patch, MagicMock
from url_generator import validate_id, get_video_urls

class TestUrlGenerator(unittest.TestCase):
    def test_validate_id(self):
        # Test valid cases
        self.assertEqual(validate_id("PL1234567890", "playlist"), "PL1234567890")
        self.assertEqual(validate_id("UU1234567890", "channel"), "UU1234567890")
        self.assertEqual(validate_id("1234567890", "video"), "1234567890")
    
        # Test invalid ID cases
        with self.assertRaises(ValueError):
            validate_id("invalid_id", "playlist")
        with self.assertRaises(ValueError):
            validate_id("invalid_id", "channel")
        with self.assertRaises(ValueError):
            validate_id("invalid@id", "video")
    
        # Test invalid type case
        with self.assertRaises(ValueError):
            validate_id("valid_id", "invalid_type")
            
    @patch('url_generator.build')
    def test_get_video_urls_playlist(self, mock_build):
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube
        mock_response = {
            'items': [{'snippet': {'resourceId': {'videoId': 'abc123'}}}],
            'nextPageToken': None
        }
        mock_youtube.playlistItems().list().execute.return_value = mock_response

        urls = get_video_urls(mock_youtube, "PL1234567890", is_playlist=True)
        self.assertEqual(urls, ["https://www.youtube.com/watch?v=abc123"])

    # Add more tests for different scenarios...

if __name__ == '__main__':
    unittest.main()