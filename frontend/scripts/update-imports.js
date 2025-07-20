const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Define the import mappings
const importMappings = [
  {
    oldPath: "from '@/stores/tax/analytics'",
    newPath: "from '@/modules/tax/store/analytics'"
  },
  {
    oldPath: "from '@/stores/tax/policy'",
    newPath: "from '@/modules/tax/store/policy'"
  },
  {
    oldPath: "from '@/stores/tax/reporting'",
    newPath: "from '@/modules/tax/store/reporting'"
  },
  {
    oldPath: "from '@/stores/gl'",
    newPath: "from '@/modules/general-ledger/store'"
  }
];

// Find all relevant files
function findFiles(dir, filePattern = /\.(js|ts|vue)$/) {
  let results = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    
    // Skip node_modules and .git directories
    if (item.isDirectory()) {
      if (['node_modules', '.git', '.next', 'dist', 'build'].includes(item.name)) {
        continue;
      }
      results = results.concat(findFiles(fullPath, filePattern));
    } else if (filePattern.test(item.name)) {
      results.push(fullPath);
    }
  }

  return results;
}

// Update imports in a single file
function updateImportsInFile(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    let updated = false;

    importMappings.forEach(({ oldPath, newPath }) => {
      if (content.includes(oldPath)) {
        const oldContent = content;
        content = content.replace(new RegExp(oldPath, 'g'), newPath);
        updated = updated || oldContent !== content;
      }
    });

    if (updated) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`Updated imports in ${filePath}`);
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error processing ${filePath}:`, error);
    return false;
  }
}

// Main function
function main() {
  const srcDir = path.join(__dirname, '..', 'src');
  const files = findFiles(srcDir);
  let updatedFiles = 0;

  console.log(`Found ${files.length} files to process...`);

  files.forEach(file => {
    if (updateImportsInFile(file)) {
      updatedFiles++;
    }
  });

  console.log(`\nUpdated imports in ${updatedFiles} files.`);
  
  // List of files/directories that can be safely removed
  const filesToRemove = [
    path.join(srcDir, 'stores', 'tax'),
    path.join(srcDir, 'stores', 'gl.ts'),
    path.join(srcDir, 'stores', 'taxPolicy.ts')
  ];

  console.log('\nThe following files/directories can be safely removed:');
  filesToRemove.forEach(file => {
    console.log(`- ${file}`);
  });

  console.log('\nPlease review the changes before committing them.');
}

// Run the script
main();
