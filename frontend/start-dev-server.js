const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const PORT = 3000;
const HOST = '0.0.0.0';
const LOG_FILE = 'dev-server.log';

// Clear previous log file
if (fs.existsSync(LOG_FILE)) {
  fs.unlinkSync(LOG_FILE);
}

// Function to log messages to console and file
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  
  // Log to console
  console.log(logMessage.trim());
  
  // Append to log file
  fs.appendFileSync(LOG_FILE, logMessage);
}

// Start the Vite dev server
log('Starting Vite development server...');
const viteProcess = spawn('npx', ['vite', '--port', PORT, '--host', HOST, '--config', 'vite.minimal.config.js'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  shell: true,
  env: {
    ...process.env,
    FORCE_COLOR: '1',
    NODE_ENV: 'development'
  }
});

// Log process output
viteProcess.stdout.on('data', (data) => {
  const output = data.toString().trim();
  log(`[Vite] ${output}`);
  
  // Check for server ready message
  if (output.includes('Local') || output.includes('Network')) {
    log('\nDevelopment server is running!');
    log(`- Local:    http://localhost:${PORT}`);
    log(`- Network:  http://${require('os').networkInterfaces().Ethernet?.[1]?.address || 'localhost'}:${PORT}`);
    log('\nPress Ctrl+C to stop the server\n');
  }
});

viteProcess.stderr.on('data', (data) => {
  const error = data.toString().trim();
  log(`[Vite Error] ${error}`);
  
  // Check for common errors
  if (error.includes('EADDRINUSE')) {
    log('\nError: Port is already in use. Please close the conflicting application or use a different port.');
  } else if (error.includes('ENOENT')) {
    log('\nError: A required file or directory is missing.');
  } else if (error.includes('EACCES')) {
    log('\nError: Permission denied. Try running with administrator privileges.');
  }
});

viteProcess.on('close', (code) => {
  log(`\nVite process exited with code ${code}`);
  if (code !== 0) {
    log('\nTroubleshooting steps:');
    log('1. Check if another process is using port 3000');
    log('2. Try deleting node_modules and running npm install again');
    log('3. Check the full error log in dev-server.log');
    log('4. Try running with a different port: `npx vite --port 3001`');
  }
});

// Handle process termination
process.on('SIGINT', () => {
  log('\nStopping development server...');
  viteProcess.kill('SIGINT');
  process.exit(0);
});
