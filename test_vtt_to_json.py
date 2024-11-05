import unittest
from vtt_to_json import deduplicate_captions, split_sentences, assign_sentence_timings
from typing import List, Dict, Tuple

class TestVTTtoJSON(unittest.TestCase):
    
    def test_deduplicate_captions_exact_duplicates(self):
        """Test that exact duplicate captions are removed."""
        captions = [
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},  # Exact duplicate
            {'text': 'Hello Universe', 'start': '00:00:03.000', 'end': '00:00:04.000'}
        ]
        expected = [
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'Hello Universe', 'start': '00:00:03.000', 'end': '00:00:04.000'}
        ]
        result = deduplicate_captions(captions)
        self.assertEqual(result, expected)
    
    def test_deduplicate_captions_consecutive_duplicates(self):
        """Test that consecutive duplicate texts are removed even if timestamps differ."""
        captions = [
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'Hello World', 'start': '00:00:03.000', 'end': '00:00:04.000'},  # Consecutive duplicate
            {'text': 'Hello Universe', 'start': '00:00:05.000', 'end': '00:00:06.000'},
            {'text': 'Hello Universe', 'start': '00:00:06.000', 'end': '00:00:07.000'},  # Consecutive duplicate
            {'text': 'Hello Galaxy', 'start': '00:00:08.000', 'end': '00:00:09.000'}
        ]
        expected = [
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'Hello Universe', 'start': '00:00:05.000', 'end': '00:00:06.000'},
            {'text': 'Hello Galaxy', 'start': '00:00:08.000', 'end': '00:00:09.000'}
        ]
        result = deduplicate_captions(captions)
        self.assertEqual(result, expected)
    
    def test_deduplicate_captions_mixed_duplicates(self):
        """Test that the function handles mixed exact and consecutive duplicates."""
        captions = [
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},  # Exact duplicate
            {'text': 'Hello World', 'start': '00:00:03.000', 'end': '00:00:04.000'},  # Consecutive duplicate
            {'text': 'Hello Universe', 'start': '00:00:05.000', 'end': '00:00:06.000'},
            {'text': 'Hello Universe', 'start': '00:00:05.000', 'end': '00:00:06.000'},  # Exact duplicate
            {'text': 'Hello Galaxy', 'start': '00:00:07.000', 'end': '00:00:08.000'},
            {'text': 'Hello Galaxy', 'start': '00:00:09.000', 'end': '00:00:10.000'},  # Not consecutive duplicate
        ]
        expected = [
            {'text': 'Hello World', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'Hello Universe', 'start': '00:00:05.000', 'end': '00:00:06.000'},
            {'text': 'Hello Galaxy', 'start': '00:00:07.000', 'end': '00:00:08.000'},
            {'text': 'Hello Galaxy', 'start': '00:00:09.000', 'end': '00:00:10.000'},
        ]
        result = deduplicate_captions(captions)
        self.assertEqual(result, expected)
    
    def test_split_sentences_basic(self):
        """Test basic sentence splitting."""
        text = "Hello World. This is a test. How are you?"
        expected = [
            "Hello World.",
            "This is a test.",
            "How are you?"
        ]
        result = split_sentences(text)
        self.assertEqual(result, expected)
    
    def test_split_sentences_with_abbreviations(self):
        """Test sentence splitting with abbreviations to prevent incorrect splits."""
        text = "Dr. Smith went to Washington D.C. He arrived at 5 p.m."
        expected = [
            "Dr. Smith went to Washington D.C.",
            "He arrived at 5 p.m."
        ]
        result = split_sentences(text)
        self.assertEqual(result, expected)
    
    def test_assign_sentence_timings_basic(self):
        """Test basic assignment of start and end times to sentences."""
        sentences = [
            ("Hello World.", 0, 12),
            ("This is a test.", 13, 29),
            ("How are you?", 30, 43)
        ]
        captions = [
            {'text': 'Hello World.', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'This is a test.', 'start': '00:00:02.000', 'end': '00:00:03.000'},
            {'text': 'How are you?', 'start': '00:00:03.000', 'end': '00:00:04.000'}
        ]
        expected = [
            {
                "id": 1,
                "text": "Hello World.",
                "start_time": "00:00:01.000",
                "end_time": "00:00:02.000"
            },
            {
                "id": 2,
                "text": "This is a test.",
                "start_time": "00:00:02.000",
                "end_time": "00:00:03.000"
            },
            {
                "id": 3,
                "text": "How are you?",
                "start_time": "00:00:03.000",
                "end_time": "00:00:04.000"
            }
        ]
        result = assign_sentence_timings(sentences, captions)
        self.assertEqual(result, expected)
    
    def test_assign_sentence_timings_overlapping_captions(self):
        """Test timing assignment when sentences span multiple captions."""
        sentences = [
            ("Hello World. This is", 0, 25),
            ("a test.", 26, 33),
            ("How are you?", 34, 47)
        ]
        captions = [
            {'text': 'Hello World. This is', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            {'text': 'a test.', 'start': '00:00:02.000', 'end': '00:00:03.000'},
            {'text': 'How are you?', 'start': '00:00:03.000', 'end': '00:00:04.000'}
        ]
        expected = [
            {
                "id": 1,
                "text": "Hello World. This is",
                "start_time": "00:00:01.000",
                "end_time": "00:00:02.000"
            },
            {
                "id": 2,
                "text": "a test.",
                "start_time": "00:00:02.000",
                "end_time": "00:00:03.000"
            },
            {
                "id": 3,
                "text": "How are you?",
                "start_time": "00:00:03.000",
                "end_time": "00:00:04.000"
            }
        ]
        result = assign_sentence_timings(sentences, captions)
        self.assertEqual(result, expected)
    
    def test_assign_sentence_timings_missing_timings(self):
        """Test fallback timings when exact timings are not found."""
        sentences = [
            ("Hello World.", 0, 12),
            ("This is a test.", 13, 29),
            ("How are you?", 30, 43)
        ]
        captions = [
            {'text': 'Hello World.', 'start': '00:00:01.000', 'end': '00:00:02.000'},
            # Missing this caption for "This is a test."
            {'text': 'How are you?', 'start': '00:00:03.000', 'end': '00:00:04.000'}
        ]
        expected = [
            {
                "id": 1,
                "text": "Hello World.",
                "start_time": "00:00:01.000",
                "end_time": "00:00:02.000"
            },
            {
                "id": 2,
                "text": "This is a test.",
                "start_time": "00:00:01.000",  # Fallback to first caption
                "end_time": "00:00:04.000"     # Fallback to last caption
            },
            {
                "id": 3,
                "text": "How are you?",
                "start_time": "00:00:03.000",
                "end_time": "00:00:04.000"
            }
        ]
        result = assign_sentence_timings(sentences, captions)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()