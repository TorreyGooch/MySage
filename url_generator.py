import os
import sys
import logging
import time
import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_id(id_value, id_type):
    if id_type not in ["playlist", "channel", "video"]:
        raise ValueError(f"Invalid id_type: {id_type}. Must be 'playlist', 'channel', or 'video'.")
    
    # Existing validation logic for each type
    if id_type == "playlist" and not id_value.startswith("PL"):
        raise ValueError("Invalid playlist ID. Must start with 'PL'.")
    elif id_type == "channel" and not id_value.startswith("U"):
        raise ValueError("Invalid channel ID. Must start with 'U'.")
    elif id_type == "video" and not id_value.isalnum():
        raise ValueError("Invalid video ID. Must be alphanumeric.")
    
    return id_value

def get_video_urls(youtube, id, is_playlist=True):
    """
    Fetch video URLs from a YouTube playlist or channel.

    Args:
    youtube (googleapiclient.discovery.Resource): YouTube API client
    id (str): Playlist or Channel ID
    is_playlist (bool): True if fetching from playlist, False if from channel

    Returns:
    list: List of video URLs
    """
    video_urls = []
    next_page_token = None
    
    with tqdm(desc="Fetching URLs", unit=" videos") as pbar:
        while True:
            try:
                if is_playlist:
                    request = youtube.playlistItems().list(
                        part="snippet",
                        playlistId=id,
                        maxResults=50,
                        pageToken=next_page_token
                    )
                else:
                    request = youtube.search().list(
                        part="id",
                        channelId=id,
                        type="video",
                        maxResults=50,
                        pageToken=next_page_token
                    )
                
                response = request.execute()
                
                for item in response['items']:
                    if is_playlist:
                        video_id = item['snippet']['resourceId']['videoId']
                    else:
                        video_id = item['id']['videoId']
                    video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
                    pbar.update(1)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Rate limiting
                time.sleep(1)
            except HttpError as e:
                logger.error(f"An HTTP error occurred: {e}")
                break
    
    return video_urls


def main():
    parser = argparse.ArgumentParser(description="Generate a list of YouTube video URLs from a playlist or channel.")
    parser.add_argument("id_type", choices=["playlist", "channel"], help="Type of ID (playlist or channel)")
    parser.add_argument("id_value", help="Playlist or Channel ID")
    parser.add_argument("-o", "--output", default="urls.txt", help="Output file name (default: urls.txt)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        logger.error("YOUTUBE_API_KEY environment variable not set")
        sys.exit(1)
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Pass both id_value and id_type to validate_id
        id_value = validate_id(args.id_value, args.id_type)
        logger.info(f"Fetching URLs for {args.id_type} with ID: {id_value}")
        
        urls = get_video_urls(youtube, id_value, is_playlist=(args.id_type == 'playlist'))
        
        with open(args.output, 'w') as f:
            for url in urls:
                f.write(f"{url}\n")
        
        logger.info(f"Successfully wrote {len(urls)} URLs to {args.output}")
    
    except HttpError as e:
        logger.error(f"An HTTP error occurred: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        sys.exit(1)

# Run the script
if __name__ == "__main__":
    main()