import yt_dlp
import os
import sys

def download_subtitles(url, output_dir):
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitlesformat': 'vtt',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            # Adjust to check for the correct subtitle filename with language code
            subtitle_filename = f"{video_id}.en.vtt"  # Assuming 'en' is the language code
            subtitle_path = os.path.join(output_dir, subtitle_filename)
            
            if os.path.exists(subtitle_path):
                print(f"Subtitles downloaded for video {video_id}")
                return True
            else:
                print(f"No subtitles available for video {video_id}")
                return False
    except Exception as e:
        print(f"Error downloading subtitles for {url}: {str(e)}")
        return False
    
def main():
    if len(sys.argv) != 2:
        print("Usage: python subtitle_downloader.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = "subtitles"
    failed_urls_file = "failed_urls.txt"

    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r") as f:
        urls = f.read().splitlines()

    failed_urls = []

    for url in urls:
        success = download_subtitles(url, output_dir)
        if not success:
            failed_urls.append(url)

    if failed_urls:
        with open(failed_urls_file, "w") as f:
            for url in failed_urls:
                f.write(f"{url}\n")
        print(f"Failed URLs saved to {failed_urls_file}")

if __name__ == "__main__":
    main()