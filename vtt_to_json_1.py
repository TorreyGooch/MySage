import re
import json
import spacy
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    filename='vtt_processing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

nlp = spacy.load('en_core_web_sm')

def parse_timestamp(timestamp):
    """Convert timestamp to standardized format"""
    return re.sub(r'\.(\d{3})\d*', r'.\1', timestamp)

def clean_text(text):
    """Remove VTT formatting tags, clean text, and remove duplicates"""
    # Remove timing tags
    text = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', text)
    # Remove formatting tags
    text = re.sub(r'</?[^>]+>', '', text)
    # Clean extra whitespace
    text = ' '.join(text.split())
    # Remove duplicate phrases
    phrases = text.split(' and ')
    unique_phrases = []
    for phrase in phrases:
        if phrase not in unique_phrases:
            unique_phrases.append(phrase)
    return ' and '.join(unique_phrases)

def process_directory(input_dir, output_dir):
    """Process all VTT files in a directory and save JSON files to output directory"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process all VTT files
    for vtt_file in input_path.glob('*.vtt'):
        try:
            # Process the file
            output = process_vtt_file(vtt_file)
            
            # Save to JSON file in output directory
            json_path = output_path / f"{output['video_id']}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
                
            logging.info(f"Saved JSON for {vtt_file.name} to {json_path}")
            
        except Exception as e:
            logging.error(f"Failed to process {vtt_file.name}: {str(e)}")

def process_vtt_file(file_path):
    """Process a single VTT file into structured JSON"""
    try:
        # Initialize variables at the start
        segments = []
        current_text = []
        current_start = None
        current_end = None
        video_id = Path(file_path).stem.split('.')[0]

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Debug: Print first 500 characters of raw content
        logging.debug(f"Raw content start:\n{content[:500]}")
        
        # Skip VTT header
        content = re.sub(r'^WEBVTT\n(?:[^\n]*\n)*\n', '', content)
        
        # Debug: Print first 500 characters after header removal
        logging.debug(f"Content after header removal:\n{content[:500]}")
        
        lines = content.split('\n')
        
        # Debug: Print first few lines
        for i, line in enumerate(lines[:10]):
            logging.debug(f"Line {i}: '{line}'")
            # Test timestamp pattern directly
            if re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line):
                logging.debug(f"Found timestamp match in line {i}")

        # Rest of the function remains the same...
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
                
            # Parse timestamp lines
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line)
            if timestamp_match:
                if current_text and current_start:
                    segments.append({
                        'text': ' '.join(current_text),
                        'start': current_start,
                        'end': current_end
                    })
                
                current_start = parse_timestamp(timestamp_match.group(1))
                current_end = parse_timestamp(timestamp_match.group(2))
                current_text = []
                
                # Get the text line(s) following the timestamp
                i += 1
                while i < len(lines) and lines[i].strip() and not re.match(r'\d{2}:\d{2}:\d{2}', lines[i]):
                    line_text = lines[i].strip()
                    if line_text and line_text not in current_text:  # Only add if not already present
                        current_text.append(line_text)
                    i += 1
                continue
            
            i += 1
            
        # Add the last segment if there is one
        if current_text and current_start:
            segments.append({
                'text': ' '.join(current_text),
                'start': current_start,
                'end': current_end
            })

        # After parsing segments, before creating sentences
        if not segments:
            raise ValueError("No valid timestamps found in VTT file")

        # Combine all text and create one sentence
        all_text = ' '.join(seg['text'] for seg in segments)
        first_start = segments[0]['start']
        last_end = segments[-1]['end']
        
        sentences = [{
            "id": 1,
            "text": all_text,
            "start_time": first_start,
            "end_time": last_end
        }]

        output = {
            "video_id": video_id,
            "sentences": sentences
        }

        return output

    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python vtt_to_json.py <input_directory> <output_directory>")
        sys.exit(1)
    
    process_directory(sys.argv[1], sys.argv[2])