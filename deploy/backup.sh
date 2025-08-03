#!/bin/bash
# Backup script to run via cron

BACKUP_DIR="/opt/hyperliquid-backtest/backups"
DATA_DIR="/opt/hyperliquid-backtest"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup current data files
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" \
    -C "$DATA_DIR" \
    "backtest_data_current.json" \
    "backtest_data_*.json" \
    "backtest_processed_*.csv" \
    2>/dev/null

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

# Optional: sync to object storage (Digital Ocean Spaces)
# s3cmd put "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" s3://your-bucket/backups/