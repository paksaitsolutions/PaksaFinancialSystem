#!/bin/bash
# Backup and disaster recovery script for Paksa Financial System

set -e

# Configuration
DB_NAME="paksa_financial"
DB_USER="postgres"
BACKUP_DIR="/backups"
S3_BUCKET="paksa-financial-backups"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Database backup
echo "Starting database backup..."
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
gzip $BACKUP_DIR/db_backup_$TIMESTAMP.sql

# Application files backup
echo "Backing up application files..."
tar -czf $BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz /app --exclude=/app/logs --exclude=/app/tmp

# Upload to S3 (if configured)
if command -v aws &> /dev/null; then
    echo "Uploading to S3..."
    aws s3 cp $BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz s3://$S3_BUCKET/database/
    aws s3 cp $BACKUP_DIR/app_backup_$TIMESTAMP.tar.gz s3://$S3_BUCKET/application/
fi

# Cleanup old backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed successfully at $TIMESTAMP"