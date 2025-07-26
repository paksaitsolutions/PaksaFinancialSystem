const express = require('express');
const path = require('path');
const fs = require('fs');
const rateLimit = require('express-rate-limit');

const app = express();
// Trust proxy headers for correct rate limiting behind reverse proxy/Docker
app.set('trust proxy', 1);
const PORT = 3000;

// Serve static files from the dist directory if it exists, otherwise from the current directory
const staticPath = fs.existsSync(path.join(__dirname, 'dist')) 
  ? path.join(__dirname, 'dist')
  : __dirname;

app.use(express.static(staticPath));

// Configure rate limiter: maximum of 100 requests per 15 minutes
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
});
// Apply rate limiter globally before any routes
app.use(limiter);

// Handle SPA routing - serve index.html for all routes
app.get('*', (req, res) => {
  // Try to serve index.html from dist first, then fallback to root
  const indexPath = fs.existsSync(path.join(staticPath, 'index.html'))
    ? path.join(staticPath, 'index.html')
    : path.join(__dirname, 'index.html');
  
  if (fs.existsSync(indexPath)) {
    res.sendFile(indexPath);
  } else {
    res.status(404).send(`
      <!DOCTYPE html>
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
            .error { color: #e74c3c; }
            code { 
              background: #f8f9fa; 
              padding: 2px 5px; 
              border-radius: 3px; 
              font-family: monospace;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>Paksa Financial System</h1>
            <p class="error">Development server is not running or index.html is missing</p>
            <p>To start the development server, run the following commands in your terminal:</p>
            <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: left; overflow-x: auto;">
cd "d:/Paksa Financial System/frontend"
npm install
npm run dev
            </pre>
            <p>Then refresh this page or go to <a href="http://localhost:3000">http://localhost:3000</a></p>
          </div>
        </body>
      </html>
    `);
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
  console.log(`Serving files from: ${staticPath}`);
});
