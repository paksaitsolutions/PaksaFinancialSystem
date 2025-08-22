#!/bin/bash
# Disaster recovery restore script

set -e

# Configuration
DB_NAME="paksa_financial"
DB_USER="postgres"
BACKUP_DIR="/backups"

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Available backups:"
    ls -la $BACKUP_DIR/db_backup_*.sql.gz
    exit 1
fi

TIMESTAMP=$1

# Verify backup files exist
DB_BACKUP="$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"
APP_BACKUP="$BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz"

if [ ! -f "$DB_BACKUP" ]; then
    echo "Database backup file not found: $DB_BACKUP"
    exit 1
fi

# Stop application
echo "Stopping application..."
systemctl stop paksa-financial || true

# Restore database
echo "Restoring database..."
dropdb -h localhost -U $DB_USER $DB_NAME || true
createdb -h localhost -U $DB_USER $DB_NAME
gunzip -c $DB_BACKUP | psql -h localhost -U $DB_USER -d $DB_NAME

# Restore application files (if exists)
if [ -f "$APP_BACKUP" ]; then
    echo "Restoring application files..."
    tar -xzf $APP_BACKUP -C /
fi

# Start application
echo "Starting application..."
systemctl start paksa-financial

echo "Restore completed successfully from backup $TIMESTAMP"