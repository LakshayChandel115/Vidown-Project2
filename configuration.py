import os

# Configuration for Render deployment
TEMP_DOWNLOAD_DIR = os.path.join(os.getcwd(), 'temp_downloads')
os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)

# Redis configuration for Render
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')