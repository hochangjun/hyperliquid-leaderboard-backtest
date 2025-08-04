import asyncio
import aiohttp
import requests
import json

async def check_active_vs_inactive_traders():
    """Compare active vs inactive top PNL traders"""
    
    # Get top 50 traders by PNL
    leaderboard_response = requests.post(
        "http://localhost:3000/leaderboard",
        json={"limit": 50}
    )
    traders = [t["ethAddress"] for t in leaderboard_response.json()["leaderboardRows"]]
    
    print(f"🔍 Checking activity status of top 50 PNL traders:\n")
    
    active_traders = []
    inactive_traders = []
    
    async with aiohttp.ClientSession() as session:
        for i, trader in enumerate(traders):
            try:
                # Get trader's positions
                payload = {"type": "clearinghouseState", "user": trader}
                async with session.post("https://api.hyperliquid.xyz/info", json=payload) as response:
                    data = await response.json()
                
                # Check if trader has any open positions
                has_positions = False
                btc_position = 0
                eth_position = 0
                total_positions = 0
                
                if "assetPositions" in data:
                    for pos in data["assetPositions"]:
                        size = float(pos["position"]["szi"])
                        if size != 0.0:
                            has_positions = True
                            total_positions += 1
                            
                            if pos["position"]["coin"] == "BTC":
                                btc_position = size
                            elif pos["position"]["coin"] == "ETH":
                                eth_position = size
                
                status = "🟢 ACTIVE" if has_positions else "🔴 INACTIVE"
                
                print(f"#{i+1:2d} {trader[:10]}... {status}")
                if has_positions:
                    print(f"     Positions: {total_positions} assets")
                    if btc_position != 0:
                        print(f"     BTC: {btc_position:.4f} ({'LONG' if btc_position > 0 else 'SHORT'})")
                    if eth_position != 0:
                        print(f"     ETH: {eth_position:.4f} ({'LONG' if eth_position > 0 else 'SHORT'})")
                    active_traders.append(trader)
                else:
                    print(f"     No open positions")
                    inactive_traders.append(trader)
                
                print()
                
            except Exception as e:
                print(f"#{i+1:2d} {trader[:10]}... ❌ ERROR: {e}")
                inactive_traders.append(trader)  # Count errors as inactive
    
    print(f"\n=== SUMMARY ===")
    print(f"🟢 Active traders (with positions): {len(active_traders)}")
    print(f"🔴 Inactive traders (no positions): {len(inactive_traders)}")
    print(f"📊 Activity rate: {len(active_traders)/len(traders)*100:.1f}%")
    
    if len(active_traders) < 100:
        print(f"\n⚠️  Only {len(active_traders)} active traders found in top 50.")
        print(f"   The script will need to check top {100 * 50 // len(active_traders) if active_traders else 200}+ traders to find 100 active ones.")

asyncio.run(check_active_vs_inactive_traders())