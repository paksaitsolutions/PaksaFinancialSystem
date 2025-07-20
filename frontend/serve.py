import http.server
import socketserver
import os
import webbrowser

PORT = 3000
DIRECTORY = 'public'

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        # Custom logging to make it cleaner
        pass

# Ensure the public directory exists
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)
    print(f"Created {DIRECTORY} directory")

# Create a simple index.html if it doesn't exist
index_path = os.path.join(DIRECTORY, 'index.html')
if not os.path.exists(index_path):
    with open(index_path, 'w') as f:
        f.write('''<!DOCTYPE html>
<html>
<head>
    <title>Paksa Financial System</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px; 
            background: #f5f5f5;
        }
        .container { 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        h1 { color: #2c3e50; }
        .status { 
            background: #e8f4fd; 
            padding: 15px; 
            border-radius: 4px; 
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Paksa Financial System</h1>
        <p>Development server is running!</p>
        <div class="status">
            <p>This is a temporary development server.</p>
            <p>To start the actual application, run:</p>
            <pre>npm run dev</pre>
        </div>
    </div>
</body>
</html>''')
    print("Created default index.html")

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Serving files from: {os.path.abspath(DIRECTORY)}")
    print("Press Ctrl+C to stop")
    
    try:
        # Open the browser automatically
        webbrowser.open(f'http://localhost:{PORT}')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
        print("Server stopped")
