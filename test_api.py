#!/usr/bin/env python3
import requests
import json

# Test the API endpoints
print("Testing API endpoints...")

# Test traders endpoint
print("\n1. Testing /api/traders endpoint:")
response = requests.get("http://167.172.74.216:8000/api/traders")
if response.ok:
    traders = response.json()
    print(f"   - Found {len(traders)} traders")
    if traders:
        # Show first trader with positions
        for trader in traders[:5]:
            if trader.get('btc_position') or trader.get('eth_position'):
                print(f"\n   Trader: {trader['ethAddress'][:10]}...")
                print(f"   - BTC Position: {trader.get('btc_position', 0)} BTC (${trader.get('btc_position_usd', 0):,.2f})")
                print(f"   - ETH Position: {trader.get('eth_position', 0)} ETH (${trader.get('eth_position_usd', 0):,.2f})")
                break
        else:
            print("   ⚠️  No traders have position data")
else:
    print(f"   ❌ Error: {response.status_code}")

# Test current data structure
print("\n2. Testing /api/current-data endpoint:")
response = requests.get("http://167.172.74.216:8000/api/current-data")
if response.ok:
    data = response.json()
    print(f"   - Timestamp: {data.get('timestamp')}")
    print(f"   - Has trader_positions: {'trader_positions' in data}")
    if 'trader_positions' in data:
        positions = data['trader_positions']
        print(f"   - Number of traders with positions: {len(positions)}")
        # Show sample position
        for addr, pos in list(positions.items())[:1]:
            print(f"\n   Sample position for {addr[:10]}...:")
            print(f"   {json.dumps(pos, indent=2)}")
else:
    print(f"   ❌ Error: {response.status_code}")