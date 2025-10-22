from flask import Flask, request, jsonify, send_file
from tasks import download_video, download_records
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video Downloader</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .form-group {
                margin-bottom: 15px;
            }
            input[type="text"], select {
                width: 100%;
                padding: 8px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .download-btn {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            .download-btn:hover {
                background-color: #45a049;
            }
            #status-message {
                margin-top: 20px;
                padding: 10px;
                border-radius: 4px;
                display: none;
            }
            .success {
                background-color: #dff0d8;
                color: #3c763d;
                border: 1px solid #d6e9c6;
            }
            .pending {
                background-color: #fcf8e3;
                color: #8a6d3b;
                border: 1px solid #faebcc;
            }
            .error {
                background-color: #f2dede;
                color: #a94442;
                border: 1px solid #ebccd1;
            }
            .warning {
                color: #dc3545;
                padding: 10px;
                border: 1px solid #dc3545;
                border-radius: 4px;
                margin-bottom: 20px;
                background-color: #fff8f8;
            }
            .note {
                color: #0056b3;
                font-size: 0.9em;
                margin-top: 10px;
            }
            .download-link {
                display: inline-block;
                padding: 8px 15px;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin-top: 10px;
            }
            .download-link:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎥 Video Downloader</h1>
            <div class="warning">
                ⚠️ Use only for public domain/own content or when you have rights.
            </div>
            <div class="note">
                📝 Note: Downloaded files will be available for 30 minutes only.
            </div>
            <form id="download-form">
                <div class="form-group">
                    <label for="url">Video URL:</label>
                    <input type="text" id="url" name="url" placeholder="Enter video URL" required>
                </div>
                <div class="form-group">
                    <label for="quality">Select Quality:</label>
                    <select id="quality" name="quality" required>
                        <option value="1">Best Quality (1080p or higher)</option>
                        <option value="2">720p</option>
                        <option value="3">480p</option>
                        <option value="4">360p</option>
                    </select>
                </div>
                <button type="submit" class="download-btn" id="downloadBtn">Download Video</button>
            </form>
            <div id="status-message"></div>
        </div>

        <script>
        const form = document.getElementById('download-form');
        const statusMsg = document.getElementById('status-message');
        const downloadBtn = document.getElementById('downloadBtn');

        form.onsubmit = function(e) {
            e.preventDefault();
            statusMsg.style.display = 'block';
            statusMsg.innerHTML = '⏳ Starting download...';
            statusMsg.className = 'pending';
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '⏳ Processing...';

            const formData = new FormData(this);
            
            fetch('/download', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                const taskId = data.split(': ')[1];
                checkStatus(taskId);
            })
            .catch(error => {
                statusMsg.innerHTML = '❌ Failed to start download';
                statusMsg.className = 'error';
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = 'Try Again';
            });
        };

        function checkStatus(taskId) {
            fetch(`/status/${taskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.state === 'SUCCESS') {
                    statusMsg.innerHTML = `✅ Download completed! <a href="/download-file/${data.result.file_id}" class="download-link">Click here to download</a>`;
                    statusMsg.className = 'success';
                    downloadBtn.innerHTML = '✅ Download Successful';
                    downloadBtn.disabled = false;
                } else if (data.state === 'FAILURE') {
                    statusMsg.innerHTML = '❌ Download failed: ' + data.status;
                    statusMsg.className = 'error';
                    downloadBtn.innerHTML = 'Try Again';
                    downloadBtn.disabled = false;
                } else {
                    statusMsg.innerHTML = '⏳ Downloading video...';
                    statusMsg.className = 'pending';
                    setTimeout(() => checkStatus(taskId), 2000);
                }
            })
            .catch(error => {
                statusMsg.innerHTML = '❌ Error checking status';
                statusMsg.className = 'error';
                downloadBtn.innerHTML = 'Try Again';
                downloadBtn.disabled = false;
            });
        }
        </script>
    </body>
    </html>
    '''

@app.route('/download', methods=['POST'])
def start_download():
    try:
        url = request.form.get('url')
        quality = request.form.get('quality')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        if not quality:
            quality = '1'  # Default to best quality
            
        if not url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL format'}), 400
            
        task = download_video.delay(url, quality)
        return f"Download started! Task ID: {task.id}"
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': 'Failed to start download'}), 500

@app.route('/status/<task_id>')
def check_status(task_id):
    task = download_video.AsyncResult(task_id)
    response = {
        'state': task.state,
        'status': 'Unknown status'
    }
    
    try:
        if task.state == 'PENDING':
            response['status'] = 'Download starting...'
        elif task.state == 'SUCCESS':
            response['result'] = task.result
        elif task.state == 'FAILURE':
            response['status'] = str(task.result)
        else:
            response['status'] = 'Download in progress...'
    except Exception as e:
        response['state'] = 'FAILURE'
        response['status'] = str(e)
    
    return jsonify(response)

@app.route('/download-file/<file_id>')
def download_file(file_id):
    try:
        if file_id not in download_records:
            return "File not found or expired", 404
            
        file_info = download_records[file_id]
        if not os.path.exists(file_info['path']):
            return "File not found", 404
            
        return send_file(
            file_info['path'],
            as_attachment=True,
            download_name=f"{file_info['title']}.{file_info['extension']}"
        )
    except Exception as e:
        print(f"File download error: {str(e)}")
        return "Error downloading file", 500

if __name__ == '__main__':
    app.run(debug=True)