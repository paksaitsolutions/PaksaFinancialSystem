// Debug script to help identify issues
console.log('Debug script loaded');

// Add global error handler
window.addEventListener('error', (event) => {
  console.error('Global error caught:', event.error);
});

// Add unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

export default {
  init() {
    console.log('Debug initialized');
  }
};