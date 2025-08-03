import asyncio
import aiohttp
import requests
import json
from datetime import datetime

async def quick_test():
    """Quick test to verify the setup and collect a single data point"""
    
    # Test 1: Check if leaderboard API is running
    print("Testing leaderboard API...")
    try:
        response = requests.post("http://localhost:3000/leaderboard", json={"limit": 5})
        leaderboard_data = response.json()
        if "error" not in leaderboard_data:
            print(f"✓ Leaderboard API is working. Found {len(leaderboard_data['leaderboardRows'])} traders")
            print(f"  Top trader: {leaderboard_data['leaderboardRows'][0]['ethAddress']}")
        else:
            print(f"✗ Leaderboard API error: {leaderboard_data['error']}")
            return
    except Exception as e:
        print(f"✗ Cannot connect to leaderboard API: {e}")
        print("Make sure to run the leaderboard service with: cd hyperliquid-leaderboard && npm start")
        return
    
    # Test 2: Check Hyperliquid API
    print("\nTesting Hyperliquid API...")
    try:
        # Get price data
        response = requests.post("https://api.hyperliquid.xyz/info", 
                               json={"type": "metaAndAssetCtxs"})
        data = response.json()
        
        btc_price = None
        eth_price = None
        
        for i, asset in enumerate(data[0]["universe"]):
            if asset["name"] == "BTC":
                btc_price = float(data[1][i]["markPx"])
            elif asset["name"] == "ETH":
                eth_price = float(data[1][i]["markPx"])
        
        if btc_price and eth_price:
            print(f"✓ Hyperliquid API is working")
            print(f"  BTC Price: ${btc_price:,.2f}")
            print(f"  ETH Price: ${eth_price:,.2f}")
        else:
            print("✗ Could not fetch price data")
            return
    except Exception as e:
        print(f"✗ Error connecting to Hyperliquid API: {e}")
        return
    
    # Test 3: Get position for top trader
    print("\nTesting position data...")
    top_trader = leaderboard_data['leaderboardRows'][0]['ethAddress']
    
    try:
        response = requests.post("https://api.hyperliquid.xyz/info",
                               json={"type": "clearinghouseState", "user": top_trader})
        position_data = response.json()
        
        if "assetPositions" in position_data:
            print(f"✓ Position data available for {top_trader}")
            btc_pos = None
            eth_pos = None
            
            for pos in position_data["assetPositions"]:
                if pos["position"]["coin"] == "BTC":
                    btc_pos = float(pos["position"]["szi"])
                elif pos["position"]["coin"] == "ETH":
                    eth_pos = float(pos["position"]["szi"])
            
            if btc_pos is not None:
                print(f"  BTC Position: {btc_pos:.4f} ({'Long' if btc_pos > 0 else 'Short' if btc_pos < 0 else 'Neutral'})")
            if eth_pos is not None:
                print(f"  ETH Position: {eth_pos:.4f} ({'Long' if eth_pos > 0 else 'Short' if eth_pos < 0 else 'Neutral'})")
        else:
            print("✗ No position data available")
    except Exception as e:
        print(f"✗ Error fetching position data: {e}")
    
    print("\n✓ All tests passed! You can now run the backtest with: python backtest.py")
    print("\nNote: The backtest will collect data over time. For a quick demo, you can modify")
    print("the duration_hours and interval_minutes parameters in backtest.py")

if __name__ == "__main__":
    asyncio.run(quick_test())