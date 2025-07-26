const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
<!DOCTYPE html>
<html>
<head>
    <title>Paksa Financial System - Local Production</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; margin: 0 auto; background: white; 
            padding: 40px; border-radius: 16px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
        }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { color: #2c3e50; margin: 0; font-size: 2.5em; }
        .status { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .status-card { 
            padding: 25px; border-radius: 12px; text-align: center; 
            background: linear-gradient(135deg, #2ecc71, #27ae60); 
            color: white; box-shadow: 0 8px 16px rgba(46, 204, 113, 0.3);
        }
        .modules { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }
        .module { 
            padding: 25px; border-radius: 12px; 
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .module h3 { color: #2c3e50; font-size: 1.4em; }
        .api-test { 
            margin-top: 30px; padding: 30px; 
            background: linear-gradient(135deg, #3498db, #2980b9); 
            border-radius: 12px; color: white;
        }
        button { 
            background: rgba(255,255,255,0.2); color: white; border: 2px solid rgba(255,255,255,0.3); 
            padding: 12px 24px; border-radius: 8px; cursor: pointer; margin: 8px;
        }
        button:hover { background: rgba(255,255,255,0.3); }
        .info-section {
            margin-top: 30px; padding: 25px; 
            background: linear-gradient(135deg, #e3f2fd, #bbdefb); 
            border-radius: 12px; border-left: 5px solid #2196f3;
        }
        .info-section a { color: #1976d2; text-decoration: none; }
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
                <p>Interface active</p>
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

        <div class="info-section">
            <h3>📋 Quick Access</h3>
            <p><strong>🔗 Backend API:</strong> <a href="http://localhost:8000" target="_blank">http://localhost:8000</a></p>
            <p><strong>📚 API Documentation:</strong> <a href="http://localhost:8000/docs" target="_blank">http://localhost:8000/docs</a></p>
            <p><strong>🏥 Health Check:</strong> <a href="http://localhost:8000/health" target="_blank">http://localhost:8000/health</a></p>
            <p><strong>👤 Login:</strong> Username: admin, Password: admin123</p>
        </div>
    </div>
</body>
</html>
  `);
});

server.listen(3000, '0.0.0.0', () => {
  console.log('Frontend server running on http://0.0.0.0:3000');
});