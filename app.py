from flask import Flask, request, jsonify, render_template
from tasks import download_video

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>V-Down - Video Downloader</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta charset="UTF-8">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 50px;
                max-width: 600px;
                width: 100%;
                animation: fadeIn 0.5s ease-in;
            }
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .header h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header .icon {
                font-size: 3em;
                margin-bottom: 15px;
            }
            
            .header p {
                color: #666;
                font-size: 1.1em;
            }
            
            .form-group {
                margin-bottom: 30px;
            }
            
            .form-group label {
                display: block;
                color: #333;
                font-weight: 600;
                margin-bottom: 12px;
                font-size: 1em;
            }
            
            .form-group input,
            .form-group select {
                width: 100%;
                padding: 15px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                font-size: 1em;
                transition: all 0.3s ease;
                background: #f8f9fa;
            }
            
            .form-group input:focus,
            .form-group select:focus {
                outline: none;
                border-color: #667eea;
                background: white;
                box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            }
            
            .form-group input::placeholder {
                color: #aaa;
            }
            
            .download-btn {
                width: 100%;
                padding: 18px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 10px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            
            .download-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
            }
            
            .download-btn:active {
                transform: translateY(0);
            }
            
            .download-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }
            
            .btn-loader {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-top-color: white;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin-right: 8px;
                vertical-align: middle;
            }
            
            #status-message {
                margin-top: 30px;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                font-weight: 500;
                display: none;
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .success {
                background-color: #d4edda;
                color: #155724;
                border: 2px solid #c3e6cb;
                display: block;
            }
            
            .pending {
                background-color: #fff3cd;
                color: #856404;
                border: 2px solid #ffeaa7;
                display: block;
            }
            
            .error {
                background-color: #f8d7da;
                color: #721c24;
                border: 2px solid #f5c6cb;
                display: block;
            }
            
            .loader {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 3px solid rgba(0, 0, 0, 0.1);
                border-top-color: #856404;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin-right: 8px;
                vertical-align: middle;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            @media (max-width: 768px) {
                body {
                    padding: 15px;
                }
                
                .container {
                    padding: 30px 20px;
                    border-radius: 15px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .header .icon {
                    font-size: 2.5em;
                }
                
                .header p {
                    font-size: 1em;
                }
                
                .form-group input,
                .form-group select {
                    padding: 12px 15px;
                    font-size: 16px;
                }
                
                .download-btn {
                    padding: 15px;
                    font-size: 1em;
                }
                
                .form-group label {
                    font-size: 0.95em;
                }
            }
            
            @media (max-width: 480px) {
                .container {
                    padding: 25px 15px;
                }
                
                .header {
                    margin-bottom: 30px;
                }
                
                .form-group {
                    margin-bottom: 25px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="icon">🎥</div>
                <h1>V-Down</h1>
                <p>Download videos in your preferred quality</p>
            </div>
            
            <form id="download-form" action="/download" method="post">
                <div class="form-group">
                    <label for="url">📎 Video URL</label>
                    <input type="text" id="url" name="url" placeholder="Paste your video URL here..." required>
                </div>
                
                <div class="form-group">
                    <label for="quality">⚙️ Select Quality</label>
                    <select id="quality" name="quality" required>
                        <option value="1">Best Quality (1080p or higher)</option>
                        <option value="2">High Quality (720p)</option>
                        <option value="3">Medium Quality (480p)</option>
                        <option value="4">Low Quality (360p)</option>
                    </select>
                </div>
                
                <button type="submit" class="download-btn" id="download-btn">
                    <span id="btn-text">Download Video</span>
                </button>
            </form>
            
            <div id="status-message"></div>
        </div>

        <script>
        const downloadBtn = document.getElementById('download-btn');
        const btnText = document.getElementById('btn-text');
        const statusMsg = document.getElementById('status-message');
        
        document.getElementById('download-form').onsubmit = function(e) {
            e.preventDefault();
            
            // Change button to downloading state
            downloadBtn.disabled = true;
            btnText.innerHTML = '<span class="btn-loader"></span>Downloading...';
            
            const formData = new FormData(this);
            
            fetch('/download', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.text();
            })
            .then(data => {
                console.log('Response:', data);
                const taskId = data.split(': ')[1];
                if (!taskId) {
                    throw new Error('No task ID received');
                }
                statusMsg.innerHTML = '<span class="loader"></span>Processing download...';
                statusMsg.className = 'pending';
                checkStatus(taskId);
            })
            .catch(error => {
                console.error('Error:', error);
                statusMsg.innerHTML = '❌ Failed to start download: ' + error.message;
                statusMsg.className = 'error';
                downloadBtn.disabled = false;
                btnText.innerHTML = 'Download Video';
            });
        };

        function checkStatus(taskId) {
            fetch(`/status/${taskId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Status check failed');
                }
                return response.json();
            })
            .then(data => {
                console.log('Status:', data);
                if (data.state === 'SUCCESS') {
                    statusMsg.innerHTML = '✅ Download completed successfully!';
                    statusMsg.className = 'success';
                    btnText.innerHTML = '✅ Download Successful';
                    setTimeout(() => {
                        downloadBtn.disabled = false;
                        btnText.innerHTML = 'Download Video';
                    }, 3000);
                } else if (data.state === 'FAILURE') {
                    statusMsg.innerHTML = '❌ Download failed: ' + (data.status || 'Unknown error');
                    statusMsg.className = 'error';
                    downloadBtn.disabled = false;
                    btnText.innerHTML = 'Download Video';
                } else {
                    statusMsg.innerHTML = '<span class="loader"></span>Downloading...';
                    statusMsg.className = 'pending';
                    setTimeout(() => checkStatus(taskId), 2000);
                }
            })
            .catch(error => {
                console.error('Status check error:', error);
                statusMsg.innerHTML = '❌ Error checking status: ' + error.message;
                statusMsg.className = 'error';
                downloadBtn.disabled = false;
                btnText.innerHTML = 'Download Video';
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
        
        if not url or not quality:
            return jsonify({'error': 'Missing URL or quality parameter'}), 400
        
        task = download_video.delay(url, quality)
        return f"Download started! Task ID: {task.id}"
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status/<task_id>')
def check_status(task_id):
    try:
        task = download_video.AsyncResult(task_id)
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Pending...'
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'result': task.result
            }
        else:
            response = {
                'state': task.state,
                'status': str(task.info)
            }
        return jsonify(response)
    except Exception as e:
        return jsonify({'state': 'FAILURE', 'status': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)