// Debug script to check routes
console.log('=== Route Debug Info ===');
console.log('Current URL:', window.location.href);
console.log('Expected route: /gl/chart-of-accounts');

// Check if Vue Router is available
if (window.__VUE_ROUTER__) {
  console.log('Vue Router found');
  console.log('Current route:', window.__VUE_ROUTER__.currentRoute.value);
} else {
  console.log('Vue Router not found in window');
}

// Test navigation
function testChartRoute() {
  if (window.__VUE_ROUTER__) {
    window.__VUE_ROUTER__.push('/gl/chart-of-accounts');
  } else {
    window.location.href = '/gl/chart-of-accounts';
  }
}

console.log('Run testChartRoute() to navigate to Chart of Accounts');
window.testChartRoute = testChartRoute;