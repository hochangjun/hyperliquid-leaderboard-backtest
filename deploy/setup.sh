#!/bin/bash
# Digital Ocean deployment setup script

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11+ and dependencies
sudo apt-get install -y python3.11 python3.11-venv python3-pip git

# Install Node.js 18+ for the leaderboard API
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create app directory
sudo mkdir -p /opt/hyperliquid-backtest
sudo chown $USER:$USER /opt/hyperliquid-backtest

# Clone repositories
cd /opt/hyperliquid-backtest
git clone YOUR_REPO_URL .

# Set up Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up Node.js app
cd hyperliquid-leaderboard
npm install
npm run build

# Create data directory
mkdir -p /opt/hyperliquid-backtest/data

# Set up systemd services
sudo cp deploy/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload