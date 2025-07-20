const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Configure readline for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Define files and directories to remove
const itemsToRemove = [
  'src/stores/tax',
  'src/stores/gl.ts',
  'src/stores/taxPolicy.ts',
  'src/stores/ai',
  'src/stores/budget',
  'src/stores/app.ts',
  'src/stores/auth.js',
  'src/stores/auth.ts',
  'src/stores/company.ts',
  'src/stores/index.js',
  'src/stores/index.ts',
  'src/stores/menu.js',
  'src/stores/menu.ts',
  'src/stores/reports.ts'
];

// Function to delete a file or directory
function deletePath(pathToDelete) {
  try {
    if (fs.existsSync(pathToDelete)) {
      if (fs.lstatSync(pathToDelete).isDirectory()) {
        fs.rmdirSync(pathToDelete, { recursive: true });
      } else {
        fs.unlinkSync(pathToDelete);
      }
      return true;
    }
    return false;
}

// Main function
async function main() {
  console.log('=== Store Cleanup Tool ===');
  console.log('The following files and directories will be removed:');
  
  // Show what will be deleted
  let itemsExist = false;
  itemsToRemove.forEach(item => {
    const fullPath = path.join(__dirname, '..', item);
    if (fs.existsSync(fullPath)) {
      console.log(`- ${item}`);
      itemsExist = true;
    }
  });

  if (!itemsExist) {
    console.log('No files or directories to remove.');
    rl.close();
    return;
  }

  // Ask for confirmation
  rl.question('\nDo you want to proceed with the deletion? (y/N) ', async (answer) => {
    if (answer.toLowerCase() === 'y') {
      console.log('\nStarting cleanup...');
      
      // Process each item
      itemsToRemove.forEach(item => {
        const fullPath = path.join(__dirname, '..', item);
        try {
          if (deletePath(fullPath)) {
            console.log(`✓ Removed: ${item}`);
          }
        } catch (error) {
          console.error(`✗ Error removing ${item}:`, error.message);
        }
      });
      
      console.log('\nCleanup complete.');
    } else {
      console.log('\nCleanup cancelled.');
    }
    
    rl.close();
  });
}

// Handle process termination
rl.on('close', () => {
  process.exit(0);
});

// Run the script
main();
