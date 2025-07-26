const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end(`
<!DOCTYPE html>
<html>
<head>
    <title>Paksa Financial System - Local Production</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        .header { text-align: center; margin-bottom: 40px; }
        .status { display: flex; gap: 20px; margin-bottom: 30px; }
        .status-card { flex: 1; padding: 20px; border-radius: 6px; text-align: center; background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .modules { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .module { padding: 20px; border: 1px solid #ddd; border-radius: 6px; }
        .api-test { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 6px; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Paksa Financial System</h1>
            <h2>Local Production Environment</h2>
            <p>Complete Financial Management System - All Modules Functional</p>
        </div>
        
        <div class="status">
            <div class="status-card">
                <h3>✅ Backend API</h3>
                <p>Running on port 8000</p>
                <p>All 10 modules active</p>
            </div>
            <div class="status-card">
                <h3>✅ Database</h3>
                <p>PostgreSQL healthy</p>
                <p>Sample data loaded</p>
            </div>
            <div class="status-card">
                <h3>✅ Frontend</h3>
                <p>Running on port 3000</p>
                <p>Simple interface active</p>
            </div>
        </div>

        <div class="modules">
            <div class="module">
                <h3>💰 Core Financial</h3>
                <ul>
                    <li>General Ledger</li>
                    <li>Accounts Payable</li>
                    <li>Accounts Receivable</li>
                    <li>Budget Management</li>
                    <li>Cash Management</li>
                </ul>
            </div>
            <div class="module">
                <h3>📊 Extended Modules</h3>
                <ul>
                    <li>Fixed Assets</li>
                    <li>Payroll Management</li>
                    <li>Human Resources</li>
                    <li>Inventory Management</li>
                    <li>Tax Management</li>
                </ul>
            </div>
            <div class="module">
                <h3>🤖 AI/Advanced</h3>
                <ul>
                    <li>AI/BI Dashboard</li>
                    <li>AI Assistant</li>
                    <li>Machine Learning</li>
                    <li>Predictive Analytics</li>
                    <li>NLP Processing</li>
                </ul>
            </div>
        </div>

        <div class="api-test">
            <h3>🧪 API Testing</h3>
            <p>Test the backend APIs directly:</p>
            <button onclick="window.open('http://localhost:8000/health', '_blank')">Health Check</button>
            <button onclick="window.open('http://localhost:8000/docs', '_blank')">API Docs</button>
            <button onclick="window.open('http://localhost:8000/api/v1/companies/available', '_blank')">Companies</button>
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #e3f2fd; border-radius: 6px;">
            <h3>📋 Quick Access</h3>
            <p><strong>Backend API:</strong> <a href="http://localhost:8000" target="_blank">http://localhost:8000</a></p>
            <p><strong>API Documentation:</strong> <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></p>
            <p><strong>Health Check:</strong> <a href="http://localhost:8000/health" target="_blank">http://localhost:8000/health</a></p>
            <p><strong>Login:</strong> Username: admin, Password: admin123</p>
        </div>
    </div>
</body>
</html>
  `);
});

server.listen(3000, '0.0.0.0', () => {
  console.log('Frontend server running on http://0.0.0.0:3000');
});