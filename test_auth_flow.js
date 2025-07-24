// Simple test script to verify authentication flow
// Run with: node test_auth_flow.js

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';
const API_PREFIX = '/api/v1';

// Test credentials
const TEST_EMAIL = 'admin@paksa.finance';
const TEST_PASSWORD = 'changeme';

let accessToken = null;
let refreshToken = null;

async function testAuthFlow() {
  console.log('=== Testing Authentication Flow ===');
  
  try {
    // Step 1: Login
    console.log('\n1. Testing login...');
    const loginResponse = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/login`, {
      username: TEST_EMAIL,
      password: TEST_PASSWORD
    });
    
    accessToken = loginResponse.data.access_token;
    refreshToken = loginResponse.data.refresh_token;
    
    console.log('✅ Login successful');
    console.log(`Access token: ${accessToken.substring(0, 15)}...`);
    console.log(`Refresh token: ${refreshToken.substring(0, 15)}...`);
    
    // Step 2: Get user profile with access token
    console.log('\n2. Testing profile access with token...');
    const profileResponse = await axios.get(`${API_BASE_URL}${API_PREFIX}/users/me`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    
    console.log('✅ Profile access successful');
    console.log('User:', profileResponse.data);
    
    // Step 3: Test token refresh
    console.log('\n3. Testing token refresh...');
    const refreshResponse = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/refresh`, {
      refresh_token: refreshToken
    });
    
    const newAccessToken = refreshResponse.data.access_token;
    console.log('✅ Token refresh successful');
    console.log(`New access token: ${newAccessToken.substring(0, 15)}...`);
    
    // Step 4: Verify new token works
    console.log('\n4. Verifying new token works...');
    const newProfileResponse = await axios.get(`${API_BASE_URL}${API_PREFIX}/users/me`, {
      headers: { Authorization: `Bearer ${newAccessToken}` }
    });
    
    console.log('✅ New token verification successful');
    console.log('User:', newProfileResponse.data);
    
    console.log('\n✅ All authentication tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
  }
}

testAuthFlow();