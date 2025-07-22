const { createServer } = require('vite');
const path = require('path');

async function startServer() {
  console.log('Starting Vite server programmatically...');
  
  try {
    const server = await createServer({
      configFile: path.resolve(__dirname, 'vite.minimal.test.js'),
      server: {
        port: 3003,
        strictPort: true,
        open: false,
        host: true,
      },
      logLevel: 'info',
    });

    await server.listen();
    
    server.printUrls();
    console.log('Vite server is running!');
    
    // Keep the process alive
    process.stdin.on('end', () => {
      server.close().then(() => process.exit(0));
    });
    
    process.stdin.resume();
  } catch (e) {
    console.error('Failed to start Vite server:', e);
    process.exit(1);
  }
}

startServer();
