#Backgorund worker task
# This file tell celery what to do in the background.

from celery import Celery
from time import sleep
import yt_dlp
import os
#We are using redis as message broker and backend both.

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task

def download_video(video_url, quality_choice):
    

    try:
        # Map quality choice to format
        quality_mapping = {
            '1': 'best',
            '2': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '3': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '4': 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        }
        
        selected_format = quality_mapping.get(quality_choice, 'best')
        
        # Set download folder path
        download_path = r"C:\Users\Chetram\Videos\videos_folder"
        
        # Create download directory if it doesn't exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': selected_format,
            'outtmpl': f'{download_path}/%(title)s.%(ext)s',
            'progress_hooks': [lambda d: print(f'Downloading: {d["_percent_str"]} of {d["_total_bytes_str"]}')],
        }
        
        # Create yt-dlp object and download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Starting download...")
            ydl.download([video_url])
            
        print("Download completed successfully!")
        print(f"Video saved to: {download_path}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
if __name__ == "__main__":
    # Example usage
    download_video()