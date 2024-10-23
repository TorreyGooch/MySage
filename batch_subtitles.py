import os
import subprocess
import argparse

def run_subtitle_downloader_on_folder(folder_path, script_name="subtitle_generator.py"):
    # List all .txt files in the specified folder
    url_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    for file in url_files:
        file_path = os.path.join(folder_path, file)
        print(f"Processing {file_path}...")
        try:
            # Call the subtitle downloader script with the current file
            subprocess.run(["python", script_name, file_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while processing {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run subtitle downloader on all .txt files in a folder.")
    parser.add_argument("folder_path", help="Path to the folder containing text files with URLs")
    args = parser.parse_args()

    run_subtitle_downloader_on_folder(args.folder_path)

if __name__ == "__main__":
    main()