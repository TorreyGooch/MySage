import re
import json
import spacy
from pathlib import Path
import logging
import sys
from typing import List, Dict, Tuple
import webvtt

# Set up logging
logging.basicConfig(
    filename='vtt_processing.log',
    level=logging.DEBUG,  # Set to DEBUG for more granular logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logging.error("Required spaCy model 'en_core_web_sm' not found. Please install it using: python -m spacy download en_core_web_sm")
    raise

def clean_text(text: str) -> str:
    """Remove VTT formatting tags and clean text."""
    # Remove all HTML-like tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace non-breaking spaces with regular spaces
    text = text.replace('&nbsp;', ' ')
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def deduplicate_captions(captions: List[Dict]) -> List[Dict]:
    """Remove duplicate captions based on text and timestamps, and consecutive duplicate texts."""
    seen = set()
    unique_captions = []
    previous_text = None

    for caption in captions:
        identifier = (caption['start'], caption['end'], caption['text'])
        if identifier in seen:
            logging.debug(f"Exact duplicate caption skipped: {caption}")
            continue
        if previous_text and caption['text'] == previous_text:
            logging.debug(f"Consecutive duplicate caption skipped: {caption}")
            continue
        seen.add(identifier)
        unique_captions.append(caption)
        previous_text = caption['text']
    
    return unique_captions

def assign_sentence_timings(sentences: List[Tuple[str, int, int]], captions: List[Dict]) -> List[Dict]:
    """
    Assign start and end times to each sentence based on character positions.

    Args:
        sentences (List[Tuple[str, int, int]]): List of tuples containing sentence text and character start/end.
        captions (List[Dict]): List of caption dictionaries with 'text', 'start', 'end'.
    
    Returns:
        List[Dict]: List of sentence dictionaries with 'id', 'text', 'start_time', 'end_time'.
    """
    sentence_dicts = []
    for idx, (sentence, sent_start, sent_end) in enumerate(sentences, 1):
        # Initialize start and end times
        start_time = ""
        end_time = ""

        # Iterate through captions to find where the sentence starts and ends
        cumulative_length = 0
        for caption in captions:
            caption_text = caption['text'] + ' '  # Add space as it was joined with space
            caption_length = len(caption_text)
            if cumulative_length <= sent_start < cumulative_length + caption_length:
                start_time = caption['start']
            if cumulative_length <= sent_end <= cumulative_length + caption_length:
                end_time = caption['end']
                break
            cumulative_length += caption_length

        # Fallback if timings not found
        if not start_time:
            start_time = captions[0]['start']
        if not end_time:
            end_time = captions[-1]['end']

        sentence_dicts.append({
            "id": idx,
            "text": sentence.strip(),
            "start_time": start_time,
            "end_time": end_time
        })
    return sentence_dicts

def split_into_sentences(all_text: str) -> List[Tuple[str, int, int]]:
    """
    Split text into sentences and return their character positions.

    Args:
        all_text (str): The combined caption text.

    Returns:
        List[Tuple[str, int, int]]: List of sentences with their start and end character positions.
    """
    doc = nlp(all_text)
    sentences = []
    for sent in doc.sents:
        sentences.append((sent.text, sent.start_char, sent.end_char))
    return sentences

def process_vtt_file(file_path: Path) -> Dict:
    """Process a single VTT file into structured JSON."""
    try:
        logging.info(f"Starting to process file: {file_path}")
        captions = []
        video_id = file_path.stem.split('.')[0]
        
        # Parse VTT using webvtt
        for caption in webvtt.read(file_path):
            cleaned_text = clean_text(caption.text)
            if cleaned_text:
                captions.append({
                    'text': cleaned_text,
                    'start': caption.start,
                    'end': caption.end
                })
        
        logging.debug(f"Total captions parsed: {len(captions)}")
                
        # Deduplicate captions
        unique_captions = deduplicate_captions(captions)
        logging.debug(f"Unique captions after deduplication: {len(unique_captions)}")
        
        if not unique_captions:
            raise ValueError("No valid captions found after deduplication.")
        
        # Combine all caption texts
        all_text = ' '.join([caption['text'] for caption in unique_captions])
        logging.debug(f"Combined text length: {len(all_text)} characters")
        
        # Split into sentences with character positions
        sentences_with_pos = split_into_sentences(all_text)
        logging.debug(f"Total sentences split: {len(sentences_with_pos)}")
        
        # Assign timings to sentences
        sentences = assign_sentence_timings(sentences_with_pos, unique_captions)
        
        output = {
            "video_id": video_id,
            "sentences": sentences
        }
        
        logging.info(f"Successfully processed {file_path.name}")
        return output
    
    except Exception as e:
        logging.error(f"Error processing {file_path}: {e}")
        raise

def process_directory(input_dir: str, output_dir: str):
    """Process all VTT files in a directory and save JSON files."""
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Processing directory: {input_dir} -> {output_dir}")
        
        # Find all VTT files
        vtt_files = list(input_path.glob('*.vtt'))
        logging.info(f"Found {len(vtt_files)} VTT files to process.")
        
        for vtt_file in vtt_files:
            try:
                output = process_vtt_file(vtt_file)
                
                # Save to JSON
                json_path = output_path / f"{output['video_id']}.json"
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                
                logging.info(f"Successfully saved JSON to {json_path}")
                
            except Exception as e:
                logging.error(f"Failed to process {vtt_file.name}: {e}")
    
    except Exception as e:
        logging.error(f"Error processing directory {input_dir}: {e}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python vtt_to_json.py <input_directory> <output_directory>")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    output_directory = sys.argv[2]
    process_directory(input_directory, output_directory) 