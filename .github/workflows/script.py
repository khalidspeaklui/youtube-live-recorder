import os
import time
import requests
from bs4 import BeautifulSoup
import subprocess

# Replace with your YouTube channel URL
CHANNEL_URL = "https://www.youtube.com/@-jannat5777/live"
CHECK_INTERVAL = 60  # Check every 60 seconds
OUTPUT_DIR = "recordings"  # Folder to save recordings

# Create output directory if it doesn't exist
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def is_live():
    """Check if the YouTube channel is currently live."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(CHANNEL_URL, headers=headers)
        if response.status_code != 200:
            print("⚠️ Failed to fetch channel page.")
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # YouTube uses a `watch` URL when a live stream is active
        live_element = soup.find("link", {"rel": "canonical"})
        if live_element and "watch" in live_element["href"]:
            return live_element["href"]  # Return the live stream URL

    except Exception as e:
        print(f"⚠️ Error checking live status: {e}")

    return False

def record_stream(live_url):
    """Start recording the live stream using yt-dlp."""
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(OUTPUT_DIR, f"recording_{timestamp}.mp4")
    
    print(f"🎥 Live stream detected! Recording started: {live_url}")
    
    command = [
        "yt-dlp",
        "-f", "best",
        "-o", output_filename,
        live_url
    ]

    try:
        # Run yt-dlp to record the stream
        process = subprocess.Popen(command)
        return process, output_filename
    except Exception as e:
        print(f"⚠️ Error starting the recording process: {e}")
        return None, None

def main():
    """Continuously check for a live stream and record when detected."""
    recording_process = None

    while True:
        live_url = is_live()
        
        if live_url:
            if recording_process is None:
                recording_process, filename = record_stream(live_url)
            else:
                print("✅ Already recording...")
        else:
            if recording_process:
                print("⏹️ Live stream ended. Stopping recording...")
                recording_process.terminate()
                recording_process = None

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
