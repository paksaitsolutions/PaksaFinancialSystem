const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Define files and directories to remove
const itemsToRemove = [
  'src/stores/tax',
  'src/stores/gl.ts',
  'src/stores/taxPolicy.ts'
];

// Create backup directory
const backupDir = path.join(__dirname, '..', 'backups', 'old-stores');
if (!fs.existsSync(backupDir)) {
  fs.mkdirSync(backupDir, { recursive: true });
}

console.log('Backing up old store files...');

// Backup and remove each item
itemsToRemove.forEach(item => {
  const fullPath = path.join(__dirname, '..', item);
  const backupPath = path.join(backupDir, item.replace(/[\\/]/g, '-'));
  
  try {
    if (fs.existsSync(fullPath)) {
      // If it's a directory, create a zip backup
      if (fs.lstatSync(fullPath).isDirectory()) {
        console.log(`Backing up directory: ${item}`);
        execSync(`robocopy "${fullPath}" "${backupPath}\" /E`);
        console.log(`Removing directory: ${item}`);
        fs.rmSync(fullPath, { recursive: true, force: true });
      } else {
        // If it's a file, copy it to backup
        console.log(`Backing up file: ${item}`);
        fs.copyFileSync(fullPath, backupPath);
        console.log(`Removing file: ${item}`);
        fs.unlinkSync(fullPath);
      }
      console.log(`✓ ${item} has been backed up and removed`);
    }
  } catch (error) {
    console.error(`Error processing ${item}:`, error.message);
  }
});

console.log('\nCleanup complete. Backups are saved to:', backupDir);
console.log('You can delete the backup directory if everything is working correctly.');
