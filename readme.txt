# YouTube URL Generator

This Python script generates a list of YouTube video URLs from a specified playlist or channel. It's designed to be the first component in a larger Podcast Semantic Search Tool project.

## Features

- Fetches video URLs from YouTube playlists or channels
- Supports large playlists with pagination
- Handles rate limiting to avoid API quota issues
- Provides progress bar for URL fetching
- Outputs URLs to a text file

## Prerequisites

- Python 3.6+
- Google API client library
- YouTube Data API v3 credentials

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube-url-generator.git
   cd youtube-url-generator
   ```

2. Install the required packages:
   ```
   pip install google-api-python-client tqdm pytest
   ```

3. Set up your YouTube Data API credentials:
   - Go to the [Google Developers Console](https://console.developers.google.com/)
   - Create a new project or select an existing one
   - Enable the YouTube Data API v3
   - Create credentials (API Key)
   - Set the API key as an environment variable:
     ```
     export YOUTUBE_API_KEY='your-api-key-here'
     ```

## Usage

Run the script with the following command:

```
python url_generator.py <id_type> <id_value> [options]
```

Arguments:
- `id_type`: Type of ID (playlist or channel)
- `id_value`: Playlist or Channel ID

Options:
- `-o, --output`: Output file name (default: urls.txt)
- `-v, --verbose`: Enable verbose logging

Example:
```
python url_generator.py playlist PL1234567890ABCDEF -o my_playlist_urls.txt
```

## Output

The script will generate a text file (default: `urls.txt`) containing one YouTube video URL per line, formatted like this:

```
https://www.youtube.com/watch?v=video_id_1
https://www.youtube.com/watch?v=video_id_2
...
```

## Testing

To run the tests for the URL generator, use the following command:

```
pytest test_url_generator.py
```

The test file `test_url_generator.py` includes unit tests for the main functions in `url_generator.py`. It covers:

- Validation of playlist and channel IDs
- Mocked API responses for both playlist and channel URL fetching
- Error handling for invalid inputs and API errors

Make sure you have `pytest` installed (`pip install pytest`) before running the tests.

## Error Handling

The script includes basic error handling for cases such as:
- Invalid playlist or channel IDs
- API errors
- Missing API key

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This script is part of a larger Podcast Semantic Search Tool project
- Thanks to the Google API client library and YouTube Data API v3