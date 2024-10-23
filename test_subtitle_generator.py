import unittest
from unittest.mock import patch, MagicMock
import os
from subtitle_generator import download_subtitles

class TestSubtitleGenerator(unittest.TestCase):

    @patch('yt_dlp.YoutubeDL')
    def test_download_subtitles_success(self, mock_ytdl):
        # Setup mock
        mock_instance = mock_ytdl.return_value.__enter__.return_value
        mock_instance.extract_info.return_value = {'id': 'test_video_id'}
        
        # Create a temporary directory for output
        output_dir = 'test_subtitles'
        os.makedirs(output_dir, exist_ok=True)
        
        # Simulate a successful subtitle download
        with open(os.path.join(output_dir, 'test_video_id.vtt'), 'w') as f:
            f.write('Sample subtitle content')
        
        # Test
        result = download_subtitles('http://example.com/test_video', output_dir)
        self.assertTrue(result)
        
        # Cleanup
        os.remove(os.path.join(output_dir, 'test_video_id.vtt'))
        os.rmdir(output_dir)

    @patch('yt_dlp.YoutubeDL')
    def test_download_subtitles_failure(self, mock_ytdl):
        # Setup mock
        mock_instance = mock_ytdl.return_value.__enter__.return_value
        mock_instance.extract_info.return_value = {'id': 'test_video_id'}
        
        # Create a temporary directory for output
        output_dir = 'test_subtitles'
        os.makedirs(output_dir, exist_ok=True)
        
        # Ensure no subtitle file exists
        if os.path.exists(os.path.join(output_dir, 'test_video_id.vtt')):
            os.remove(os.path.join(output_dir, 'test_video_id.vtt'))
        
        # Test
        result = download_subtitles('http://example.com/test_video', output_dir)
        self.assertFalse(result)
        
        # Cleanup
        os.rmdir(output_dir)

if __name__ == '__main__':
    unittest.main()