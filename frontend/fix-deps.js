const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Update package.json scripts
const packageJsonPath = path.join(__dirname, 'package.json');
const packageJson = require(packageJsonPath);

// Update scripts to use the fixed config
packageJson.scripts = {
  ...packageJson.scripts,
  "dev": "vite --config vite.fixed.config.js",
  "build": "vite build --config vite.fixed.config.js",
  "preview": "vite preview --config vite.fixed.config.js"
};

// Save the updated package.json
fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));

console.log('Updated package.json with fixed Vite configuration');

// Remove node_modules and package-lock.json
console.log('Removing node_modules and package-lock.json...');
try {
  if (fs.existsSync(path.join(__dirname, 'node_modules'))) {
    fs.rmSync(path.join(__dirname, 'node_modules'), { recursive: true, force: true });
  }
  if (fs.existsSync(path.join(__dirname, 'package-lock.json'))) {
    fs.rmSync(path.join(__dirname, 'package-lock.json'));
  }
  console.log('Removed node_modules and package-lock.json');
} catch (err) {
  console.error('Error removing node_modules or package-lock.json:', err);
}

// Install dependencies
console.log('Installing dependencies...');
try {
  execSync('npm install', { stdio: 'inherit', cwd: __dirname });
  console.log('Dependencies installed successfully');} catch (err) {
  console.error('Error installing dependencies:', err);
  process.exit(1);
}
