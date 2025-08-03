# Digital Ocean Deployment Guide

## Data Saving Schedule
- **Every 5 minutes**: Collects new data point
- **Every hour**: Saves checkpoint to disk
- **On crash/restart**: Automatically loads last checkpoint and continues

## Quick Deploy Steps

1. **Create a Digital Ocean Droplet**
   - Ubuntu 22.04 LTS
   - At least 2GB RAM
   - 25GB disk space

2. **SSH into your droplet and run:**
```bash
# Download setup script
wget https://raw.githubusercontent.com/hochangjun/hyperliquid-leaderboard-backtest/main/deploy/setup.sh
chmod +x setup.sh

# Run setup
./setup.sh
```

3. **Configure and start services:**
```bash
# Create log directory
sudo mkdir -p /opt/hyperliquid-backtest/logs
sudo chown -R $USER:$USER /opt/hyperliquid-backtest/logs

# Enable and start services (services will run as your user)
sudo systemctl enable hyperliquid-leaderboard@$USER
sudo systemctl enable hyperliquid-backtest@$USER
sudo systemctl start hyperliquid-leaderboard@$USER
sleep 10  # Wait for API to start
sudo systemctl start hyperliquid-backtest@$USER
```

4. **Set up automated backups:**
```bash
# Add to crontab
crontab -e

# Add this line for hourly backups
0 * * * * /opt/hyperliquid-backtest/deploy/backup.sh
```

## Monitoring

Check service status:
```bash
sudo systemctl status hyperliquid-leaderboard
sudo systemctl status hyperliquid-backtest
```

View logs:
```bash
# Real-time logs
sudo journalctl -u hyperliquid-backtest -f

# Or from log files
tail -f /opt/hyperliquid-backtest/logs/backtest.log
```

Check data collection:
```bash
ls -la /opt/hyperliquid-backtest/backtest_data_*.json
```

## Recovery from Crash

The systemd services will automatically restart on crash. The backtest script will:
1. Load the most recent `backtest_data_*.json` file
2. Continue collecting from where it left off
3. Save checkpoints every hour

## Manual Recovery

If automatic recovery fails:
```bash
# Check what data you have
ls -la /opt/hyperliquid-backtest/backtest_data_*.json

# Restart services
sudo systemctl restart hyperliquid-leaderboard
sudo systemctl restart hyperliquid-backtest
```

## Data Safety Features

1. **Incremental saves**: Every hour
2. **Dual file strategy**: 
   - `backtest_data_current.json` - Always has latest data
   - `backtest_data_TIMESTAMP.json` - Timestamped backups
3. **Automatic restart**: Via systemd
4. **Backup script**: Hourly backups to compressed archives
5. **Resume capability**: Loads existing data on start