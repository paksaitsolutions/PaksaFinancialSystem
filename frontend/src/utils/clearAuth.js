// Clear all authentication data
localStorage.clear();
sessionStorage.clear();
console.log('All authentication data cleared');

// Reload the page
window.location.href = '/auth/login';