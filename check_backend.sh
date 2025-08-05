#!/bin/bash

echo "Checking backend services on Digital Ocean..."

# Check if services are running
echo -e "\n1. Checking service status:"
systemctl status hyperliquid-backtest --no-pager | head -10
systemctl status api-server --no-pager | head -10
systemctl status hyperliquid-leaderboard --no-pager | head -10

# Check if ports are listening
echo -e "\n2. Checking listening ports:"
sudo netstat -tlnp | grep -E ":(3000|8000)"

# Check firewall rules
echo -e "\n3. Checking firewall rules:"
sudo ufw status numbered

# Test API endpoints locally
echo -e "\n4. Testing API endpoints locally:"
curl -s http://localhost:8000/api/health | python3 -m json.tool
curl -s http://localhost:8000/api/traders | head -100

# Check from external
echo -e "\n5. Testing from external (this machine):"
curl -s http://167.172.74.216:8000/api/health