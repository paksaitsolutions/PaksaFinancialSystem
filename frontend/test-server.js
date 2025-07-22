const http = require('http');

const server = http.createServer((req, res) => {
  console.log(`Received request for ${req.url}`);
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Test server is running!');});

const PORT = 3003;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`Test server running at http://localhost:${PORT}/`);
  console.log('Press Ctrl+C to stop the server');
});

process.on('SIGINT', () => {
  console.log('\nShutting down server...');
  server.close(() => {
    console.log('Server stopped');
    process.exit(0);
  });
});
