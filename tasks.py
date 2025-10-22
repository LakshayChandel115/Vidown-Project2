#Backgorund worker task
# This file tell celery what to do in the background.

from celery import Celery
from time import sleep
import yt_dlp
import os
import uuid
import ssl
from datetime import datetime, timedelta

# Create Celery instance first
app = Celery('tasks')

# Configure Celery with all settings at once

app.conf.update(
    # Broker and backend URLs with proper URL encoding and default username
    broker_url='rediss://default:AU1xAAIncDIyYTQwZTQwODliYjc0YTI1OGQ5Y2ExMDg3ZmNiODZlOHAyMTk4MjU@trusted-woodcock-19825.upstash.io:6379/0',
    result_backend='rediss://default:AU1xAAIncDIyYTQwZTQwODliYjc0YTI1OGQ5Y2ExMDg3ZmNiODZlOHAyMTk4MjU@trusted-woodcock-19825.upstash.io:6379/0',
    
    # SSL settings with proper configuration
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE,
        'ssl_ca_certs': None
    },
    
    # Connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None
)

#Store file information 
download_records = {}

@app.task
def download_video(video_url, quality_choice):
    try:
        # Generate unique ID for this download
        file_id = str(uuid.uuid4())
        
        # Use just one consistent path
        base_path = os.path.join(os.getcwd(), 'temp_downloads')
        download_path = os.path.join(base_path, file_id)
        
       
        os.makedirs(download_path, exist_ok=True)

        # Map quality choice to format
        quality_mapping = {
            '1': 'best',
            '2': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '3': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '4': 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        }
        
        selected_format = quality_mapping.get(str(quality_choice), 'best')
         # Update ydl_opts with absolute path
        ydl_opts = {
            'format': selected_format,
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: print(f"Downloading...: {d.get('_percent_str','0%')} of {d.get('_total_bytes_str', 'unknown size')}")],
            'quiet': False,
            'no_warnings': False
        }
     
        
         # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info['title']
            downloaded_file = os.path.join(download_path, f"{video_title}.{info['ext']}")
        
        # Store download information
        download_records[file_id] = {
            'path': downloaded_file,
            'title': video_title,
            'timestamp': datetime.now(),
            'extension': info['ext']
        }
        # Schedule cleanup task
        cleanup_file.apply_async((file_id,), countdown=1800)  # 30 minutes
        
        return {
            'status': 'success',
            'message': 'Download completed successfully!',
            'file_id': file_id,
            'title': video_title
        }
        
    except Exception as e:
        raise Exception(str(e))
    
    
@app.task
def cleanup_file(file_id):
    if file_id in download_records:
        file_path = download_records[file_id]['path']
        if os.path.exists(file_path):
            os.remove(file_path)
            # Remove parent directory
            os.rmdir(os.path.dirname(file_path))
        del download_records[file_id]

        
if __name__ == "__main__":
    app.start()