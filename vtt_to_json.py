import re
import json
import spacy
from pathlib import Path
import logging
import traceback

# Set up logging
logging.basicConfig(
    filename='vtt_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logging.error("Required spaCy model 'en_core_web_sm' not found. Please install it using: python -m spacy download en_core_web_sm")
    raise

def parse_timestamp(timestamp):
    """Convert timestamp to standardized format"""
    # Replace comma with dot if present
    timestamp = timestamp.replace(',', '.')
    return re.sub(r'\.(\d{3})\d*', r'.\1', timestamp)

def clean_text(text):
    """Remove VTT formatting tags and clean text"""
    # Remove timing tags
    text = re.sub(r'<\d{2}:\d{2}:\d{2}[.,]\d{3}>', '', text)
    # Remove formatting tags
    text = re.sub(r'</?[^>]+>', '', text)
    # Remove non-breaking space HTML entities
    text = text.replace('&nbsp;', ' ')
    # Clean extra whitespace
    text = ' '.join(text.split())
    return text

def process_vtt_file(file_path):
    """Process a single VTT file into structured JSON"""
    try:
        logging.info(f"Starting to process file: {file_path}")
        segments = []
        seen_texts = set()  # To track already added texts
        current_text = []
        current_start = None
        current_end = None
        video_id = Path(file_path).stem.split('.')[0]

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logging.debug(f"File content length: {len(content)} characters")

        logging.debug(f"First 200 characters of content:\n{content[:200]}")

        # Remove header by splitting at the first double newline
        parts = re.split(r'\r?\n\r?\n', content, maxsplit=1)
        if len(parts) > 1:
            content = parts[1]
            logging.debug(f"Content after header removal (first 200 chars):\n{content[:200]}")
        else:
            # If no header is found, use the entire content
            logging.debug("No header found, using entire content.")

        lines = content.splitlines()
        logging.info(f"Number of lines to process: {len(lines)}")

        i = 0
        timestamp_count = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Log the current line being processed
            logging.debug(f"Processing line {i}: {line}")

            # Match timestamp line with enhanced pattern matching
            timestamp_match = re.match(r'^(\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{3})', line)
            if timestamp_match:
                timestamp_count += 1
                logging.debug(f"Found timestamp {timestamp_count}: {line}")

                # Save previous segment if exists and text is unique
                if current_text and current_start:
                    segment_text = clean_text(' '.join(current_text))
                    if segment_text not in seen_texts:
                        segments.append({
                            'text': segment_text,
                            'start': current_start,
                            'end': current_end
                        })
                        seen_texts.add(segment_text)
                        logging.debug(f"Added segment: {segments[-1]}")
                    else:
                        logging.debug(f"Duplicate segment found. Skipping: {segment_text}")

                # Start new segment
                current_start = parse_timestamp(timestamp_match.group(1))
                current_end = parse_timestamp(timestamp_match.group(2))
                current_text = []

                # Get text lines until next timestamp or empty line
                i += 1
                text_lines_found = 0
                while i < len(lines) and lines[i].strip() and not re.match(r'\d{2}:\d{2}:\d{2}', lines[i]):
                    line_text = lines[i].strip()
                    if line_text:
                        current_text.append(line_text)
                        text_lines_found += 1
                    i += 1
                logging.debug(f"Found {text_lines_found} lines of text for current timestamp")
                continue

            i += 1

        # Add final segment with logging and deduplication
        if current_text and current_start:
            segment_text = clean_text(' '.join(current_text))
            if segment_text not in seen_texts:
                segments.append({
                    'text': segment_text,
                    'start': current_start,
                    'end': current_end
                })
                seen_texts.add(segment_text)
                logging.debug(f"Added final segment: {segments[-1]}")
            else:
                logging.debug(f"Duplicate final segment found. Skipping: {segment_text}")

        # Log segment count
        logging.info(f"Total segments found: {len(segments)}")
        logging.info(f"Total timestamps found: {timestamp_count}")

        # Verify we have segments with more detailed error
        if not segments:
            error_msg = f"No valid segments found in VTT file. Found {timestamp_count} timestamps but no valid segments were created."
            logging.error(error_msg)
            raise ValueError(error_msg)

        # Combine segments into sentences
        all_text = ' '.join(seg['text'] for seg in segments)
        doc = nlp(all_text)

        # Create sentences with timing info
        sentences = []
        if segments:
            sentence_start = segments[0]['start']
            sentence_end = segments[-1]['end']

            for sent in doc.sents:
                sentences.append({
                    "id": len(sentences) + 1,
                    "text": sent.text.strip(),
                    "start_time": sentence_start,
                    "end_time": sentence_end
                })

            logging.info(f"Created {len(sentences)} sentences from {len(segments)} segments")

        output = {
            "video_id": video_id,
            "sentences": sentences
        }

        return output

    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise

def process_directory(input_dir, output_dir):
    """Process all VTT files in a directory and save JSON files"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    logging.info(f"Starting directory processing: {input_dir} -> {output_dir}")

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Process all VTT files
    vtt_files = list(input_path.glob('*.vtt'))
    logging.info(f"Found {len(vtt_files)} VTT files to process")

    for vtt_file in vtt_files:
        try:
            logging.info(f"Processing file: {vtt_file}")
            output = process_vtt_file(vtt_file)

            # Save to JSON file
            json_path = output_path / f"{output['video_id']}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            logging.info(f"Successfully processed {vtt_file.name} to {json_path}")

        except Exception as e:
            logging.error(f"Failed to process {vtt_file.name}")
            logging.error(f"Error: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python vtt_to_json.py <input_directory> <output_directory>")
        sys.exit(1)

    process_directory(sys.argv[1], sys.argv[2])