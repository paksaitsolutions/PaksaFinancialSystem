const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 Checking Vuetify installation and dependencies...');

// Check package.json
console.log('\n📦 Checking package.json...');
try {
  const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  const requiredDeps = [
    'vuetify',
    'sass',
    'sass-loader',
    '@vitejs/plugin-vue',
    'vite'
  ];
  
  console.log('\n📌 Installed Dependencies:');
  requiredDeps.forEach(dep => {
    const version = deps[dep] ? `✅ ${deps[dep]}` : '❌ Not found';
    console.log(`  ${dep.padEnd(20)} ${version}`);
  });
  
  // Check Vite config
  console.log('\n⚡ Checking Vite configuration...');
  if (fs.existsSync('vite.config.js') || fs.existsSync('vite.config.ts')) {
    console.log('  ✅ Vite config file found');
    
    // Check if Vuetify is properly configured in Vite
    const viteConfig = fs.readFileSync('vite.config.js', 'utf-8') || 
                      fs.readFileSync('vite.config.ts', 'utf-8');
    
    const hasVuetifyPlugin = viteConfig.includes('vuetify({') || 
                           viteConfig.includes('vuetify(');
    
    console.log(`  ${hasVuetifyPlugin ? '✅' : '❌'} Vuetify plugin configured in Vite`);
  } else {
    console.log('  ❌ Vite config file not found');
  }
  
  // Check main.js/ts
  console.log('\n🔧 Checking main entry file...');
  const mainFile = fs.existsSync('src/main.ts') ? 'src/main.ts' : 
                  fs.existsSync('src/main.js') ? 'src/main.js' : null;
  
  if (mainFile) {
    console.log(`  ✅ Found main entry file: ${mainFile}`);
    const mainContent = fs.readFileSync(mainFile, 'utf-8');
    const hasVuetifyImport = mainContent.includes('vuetify');
    console.log(`  ${hasVuetifyImport ? '✅' : '❌'} Vuetify import found in main file`);
  } else {
    console.log('  ❌ Could not find main entry file (main.js or main.ts)');
  }
  
  // Check Vuetify version
  console.log('\n🔄 Checking Vuetify version...');
  try {
    const vuetifyVersion = execSync('npm list vuetify', { stdio: 'pipe' }).toString().trim();
    console.log(`  ${vuetifyVersion}`);
    
    // Check for known issues with specific versions
    if (vuetifyVersion.includes('3.0.0') || vuetifyVersion.includes('3.0.1')) {
      console.log('  ⚠️  You are using an early version of Vuetify 3. Consider upgrading to the latest stable version');
    }
  } catch (e) {
    console.log('  ❌ Could not determine Vuetify version');
  }
  
  console.log('\n✅ Dependency check completed!');
  console.log('\n📝 Next steps:');
  console.log('1. Run the reset script: node reset-vite-cache.ps1');
  console.log('2. Start the development server: npm run dev');
  console.log('3. If issues persist, check the browser console for specific errors');
  
} catch (error) {
  console.error('❌ Error checking dependencies:', error.message);
  process.exit(1);
}
