import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Tuple
import asyncio
import aiohttp
from collections import defaultdict

class HyperliquidBacktest:
    def __init__(self):
        self.leaderboard_api = "http://localhost:3000/leaderboard"
        self.hyperliquid_api = "https://api.hyperliquid.xyz/info"
        self.positions_data = []
        self.price_data = []
        
    async def get_top_traders_with_positions(self, target_count: int = 100) -> List[str]:
        """Get top traders by PNL who have at least one open position"""
        try:
            # Start with more traders than we need since some might be inactive
            fetch_limit = min(target_count * 3, 500)  # Fetch up to 3x more to filter from
            
            payload = {
                "limit": fetch_limit,
                "offset": 0,
                "sort": {
                    "timePeriod": "allTime",
                    "type": "pnl",
                    "direction": "desc"
                }
            }
            
            response = requests.post(self.leaderboard_api, json=payload)
            data = response.json()
            
            if "error" in data:
                print(f"Error fetching leaderboard: {data['error']}")
                return []
            
            all_traders = [row["ethAddress"] for row in data["leaderboardRows"]]
            print(f"Fetched {len(all_traders)} traders from leaderboard, filtering for active positions...")
            
            # Check each trader for active positions
            active_traders = []
            
            async with aiohttp.ClientSession() as session:
                for i, trader in enumerate(all_traders):
                    if len(active_traders) >= target_count:
                        break
                        
                    try:
                        positions = await self.get_user_positions(session, trader)
                        
                        # Check if trader has any open positions
                        has_positions = False
                        for position in positions.get("positions", []):
                            if float(position["position"]["szi"]) != 0.0:
                                has_positions = True
                                break
                        
                        if has_positions:
                            active_traders.append(trader)
                            
                        # Progress indicator
                        if (i + 1) % 50 == 0:
                            print(f"   Checked {i + 1}/{len(all_traders)} traders, found {len(active_traders)} active")
                            
                    except Exception as e:
                        print(f"   Error checking positions for {trader}: {e}")
                        continue
            
            print(f"✅ Found {len(active_traders)} active traders with open positions")
            return active_traders[:target_count]
            
        except Exception as e:
            print(f"Error fetching active traders: {e}")
            return []
    
    async def get_user_positions(self, session: aiohttp.ClientSession, address: str) -> Dict:
        """Get current positions for a user"""
        payload = {
            "type": "clearinghouseState",
            "user": address
        }
        
        try:
            async with session.post(self.hyperliquid_api, json=payload) as response:
                data = await response.json()
                return {
                    "address": address,
                    "positions": data.get("assetPositions", []),
                    "timestamp": datetime.now()
                }
        except Exception as e:
            print(f"Error fetching positions for {address}: {e}")
            return {"address": address, "positions": [], "timestamp": datetime.now()}
    
    async def get_all_positions(self, traders: List[str]) -> List[Dict]:
        """Get positions for all traders concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_user_positions(session, trader) for trader in traders]
            positions = await asyncio.gather(*tasks)
            return positions
    
    def aggregate_positions(self, positions: List[Dict], prices: Dict[str, float]) -> Dict[str, Dict]:
        """Aggregate positions by asset (BTC, ETH) in both token and USD values"""
        aggregated = defaultdict(lambda: {
            "long_tokens": 0, "short_tokens": 0, "net_tokens": 0,
            "long_usd": 0, "short_usd": 0, "net_usd": 0,
            "count": 0
        })
        
        for trader_data in positions:
            for position in trader_data["positions"]:
                asset = position["position"]["coin"]
                if asset in ["BTC", "ETH"] and asset in prices:
                    size = float(position["position"]["szi"])
                    price = prices[asset]
                    usd_value = abs(size) * price
                    
                    if size > 0:
                        aggregated[asset]["long_tokens"] += size
                        aggregated[asset]["long_usd"] += usd_value
                    else:
                        aggregated[asset]["short_tokens"] += abs(size)
                        aggregated[asset]["short_usd"] += usd_value
                    
                    aggregated[asset]["net_tokens"] += size
                    aggregated[asset]["net_usd"] = aggregated[asset]["long_usd"] - aggregated[asset]["short_usd"]
                    aggregated[asset]["count"] += 1
        
        return dict(aggregated)
    
    async def get_price_data(self, coin: str) -> float:
        """Get current price for a coin"""
        payload = {
            "type": "metaAndAssetCtxs"
        }
        
        try:
            response = requests.post(self.hyperliquid_api, json=payload)
            data = response.json()
            
            # Find the coin in the universe array
            for i, asset in enumerate(data[0]["universe"]):
                if asset["name"] == coin:
                    # Use the same index to get the price from contexts
                    if i < len(data[1]):
                        return float(data[1][i]["markPx"])
            return 0.0
        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")
            return 0.0
    
    async def collect_data_point(self, traders: List[str]) -> Dict:
        """Collect one data point: positions and prices"""
        # Get prices first
        btc_price = await self.get_price_data("BTC")
        eth_price = await self.get_price_data("ETH")
        prices = {"BTC": btc_price, "ETH": eth_price}
        
        # Get all positions
        positions = await self.get_all_positions(traders)
        aggregated = self.aggregate_positions(positions, prices)
        
        data_point = {
            "timestamp": datetime.now(),
            "btc_price": btc_price,
            "eth_price": eth_price,
            "btc_positions": aggregated.get("BTC", {
                "long_tokens": 0, "short_tokens": 0, "net_tokens": 0,
                "long_usd": 0, "short_usd": 0, "net_usd": 0, "count": 0
            }),
            "eth_positions": aggregated.get("ETH", {
                "long_tokens": 0, "short_tokens": 0, "net_tokens": 0,
                "long_usd": 0, "short_usd": 0, "net_usd": 0, "count": 0
            })
        }
        
        return data_point
    
    async def run_backtest(self, duration_hours: int = 24, interval_minutes: int = 5):
        """Run the backtest for specified duration"""
        print(f"Starting backtest for {duration_hours} hours with {interval_minutes} minute intervals")
        print("📊 Tracking top 100 traders by PNL who have ACTIVE positions (filters out inactive accounts)")
        print("🔄 Active trader list will be refreshed every hour")
        
        # Get initial top traders with active positions
        traders = await self.get_top_traders_with_positions(100)
        if not traders:
            print("Failed to get active traders. Make sure the leaderboard API is running.")
            return
        
        # Calculate number of iterations
        iterations = (duration_hours * 60) // interval_minutes
        
        # Load existing data if any
        data_points = self.load_existing_data()
        
        for i in range(iterations):
            print(f"\nCollecting data point {i+1}/{iterations}")
            
            # Refresh top 100 active traders every hour (every 12 iterations at 5-min intervals)
            if i % 12 == 0 and i > 0:
                print("🔄 Refreshing top 100 active traders list...")
                new_traders = await self.get_top_traders_with_positions(100)
                if new_traders:
                    # Compare with previous list
                    new_addresses = set(new_traders)
                    old_addresses = set(traders)
                    added = new_addresses - old_addresses
                    removed = old_addresses - new_addresses
                    
                    if added or removed:
                        print(f"   📈 New traders in top 100: {len(added)}")
                        print(f"   📉 Traders dropped from top 100: {len(removed)}")
                        if added:
                            print(f"   ➕ Added: {list(added)[:3]}{'...' if len(added) > 3 else ''}")
                        if removed:
                            print(f"   ➖ Removed: {list(removed)[:3]}{'...' if len(removed) > 3 else ''}")
                    else:
                        print("   ✓ Top 100 list unchanged")
                    
                    traders = new_traders
                else:
                    print("   ⚠️ Failed to refresh traders, using previous list")
            
            try:
                data_point = await self.collect_data_point(traders)
                
                # Add metadata about trader list
                data_point['trader_list_updated_at'] = i // 12  # Which hour the list was last updated
                data_point['iteration'] = i + 1
                
                data_points.append(data_point)
                
                # Print current status
                print(f"Timestamp: {data_point['timestamp']}")
                print(f"BTC Price: ${data_point['btc_price']:,.2f}")
                print(f"BTC Net Position: ${data_point['btc_positions']['net_usd']:,.2f} ({data_point['btc_positions']['net_tokens']:.4f} BTC)")
                print(f"ETH Price: ${data_point['eth_price']:,.2f}")
                print(f"ETH Net Position: ${data_point['eth_positions']['net_usd']:,.2f} ({data_point['eth_positions']['net_tokens']:.4f} ETH)")
                
                # Save incrementally every 12 data points (1 hour at 5-min intervals)
                if (i + 1) % 12 == 0:
                    self.save_data(data_points)
                    print("✓ Data checkpoint saved")
                
            except Exception as e:
                print(f"Error collecting data point: {e}")
            
            # Wait for next interval (except on last iteration)
            if i < iterations - 1:
                await asyncio.sleep(interval_minutes * 60)
        
        # Final save and analyze data
        self.save_data(data_points)
        self.analyze_results(data_points)
    
    def load_existing_data(self) -> List[Dict]:
        """Load most recent data file if exists"""
        import glob
        data_files = sorted(glob.glob("backtest_data_*.json"))
        if data_files:
            with open(data_files[-1], 'r') as f:
                data = json.load(f)
                print(f"Loaded {len(data)} existing data points from {data_files[-1]}")
                return data
        return []
    
    def save_data(self, data_points: List[Dict]):
        """Save collected data to file"""
        filename = "backtest_data_current.json"
        with open(filename, 'w') as f:
            json.dump(data_points, f, default=str, indent=2)
        
        # Also save timestamped backup
        backup_filename = f"backtest_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w') as f:
            json.dump(data_points, f, default=str, indent=2)
        
        print(f"\nData saved to {filename} and {backup_filename}")
    
    def analyze_results(self, data_points: List[Dict]):
        """Analyze and visualize the results"""
        if len(data_points) < 2:
            print("Not enough data points for analysis")
            return
        
        # Convert to DataFrame for easier analysis
        df_data = []
        for dp in data_points:
            df_data.append({
                'timestamp': pd.to_datetime(dp['timestamp']),
                'btc_price': dp['btc_price'],
                'eth_price': dp['eth_price'],
                'btc_net_position_usd': dp['btc_positions']['net_usd'],
                'eth_net_position_usd': dp['eth_positions']['net_usd'],
                'btc_net_position_tokens': dp['btc_positions']['net_tokens'],
                'eth_net_position_tokens': dp['eth_positions']['net_tokens'],
                'btc_long_usd': dp['btc_positions']['long_usd'],
                'btc_short_usd': dp['btc_positions']['short_usd'],
                'eth_long_usd': dp['eth_positions']['long_usd'],
                'eth_short_usd': dp['eth_positions']['short_usd']
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        
        # Calculate price changes
        df['btc_price_change'] = df['btc_price'].pct_change()
        df['eth_price_change'] = df['eth_price'].pct_change()
        
        # Calculate position changes (using USD values)
        df['btc_position_change_usd'] = df['btc_net_position_usd'].diff()
        df['eth_position_change_usd'] = df['eth_net_position_usd'].diff()
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # BTC Analysis
        ax1 = axes[0, 0]
        ax1_twin = ax1.twinx()
        ax1.plot(df.index, df['btc_price'], 'b-', label='BTC Price')
        ax1_twin.plot(df.index, df['btc_net_position_usd'] / 1_000_000, 'r-', label='Net Position (USD)')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('BTC Price ($)', color='b')
        ax1_twin.set_ylabel('Net Position ($M)', color='r')
        ax1.set_title('BTC Price vs Top 100 Traders Net Position (USD)')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1_twin.tick_params(axis='y', labelcolor='r')
        
        # ETH Analysis
        ax2 = axes[0, 1]
        ax2_twin = ax2.twinx()
        ax2.plot(df.index, df['eth_price'], 'b-', label='ETH Price')
        ax2_twin.plot(df.index, df['eth_net_position_usd'] / 1_000_000, 'r-', label='Net Position (USD)')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('ETH Price ($)', color='b')
        ax2_twin.set_ylabel('Net Position ($M)', color='r')
        ax2.set_title('ETH Price vs Top 100 Traders Net Position (USD)')
        ax2.tick_params(axis='y', labelcolor='b')
        ax2_twin.tick_params(axis='y', labelcolor='r')
        
        # Correlation Analysis
        # Remove NaN values for correlation calculation
        btc_corr_data = df[['btc_price_change', 'btc_position_change_usd']].dropna()
        eth_corr_data = df[['eth_price_change', 'eth_position_change_usd']].dropna()
        
        if len(btc_corr_data) > 2:
            btc_correlation = btc_corr_data.corr().iloc[0, 1]
            eth_correlation = eth_corr_data.corr().iloc[0, 1]
            
            # Scatter plots
            ax3 = axes[1, 0]
            ax3.scatter(btc_corr_data['btc_position_change_usd'] / 1_000_000, btc_corr_data['btc_price_change'] * 100)
            ax3.set_xlabel('Position Change ($M)')
            ax3.set_ylabel('Price Change %')
            ax3.set_title(f'BTC Position Change vs Price Change\nCorrelation: {btc_correlation:.3f}')
            
            ax4 = axes[1, 1]
            ax4.scatter(eth_corr_data['eth_position_change_usd'] / 1_000_000, eth_corr_data['eth_price_change'] * 100)
            ax4.set_xlabel('Position Change ($M)')
            ax4.set_ylabel('Price Change %')
            ax4.set_title(f'ETH Position Change vs Price Change\nCorrelation: {eth_correlation:.3f}')
            
            # Print summary statistics
            print("\n=== BACKTEST RESULTS ===")
            print(f"Data points collected: {len(df)}")
            print(f"Duration: {df.index[-1] - df.index[0]}")
            print(f"\nBTC Analysis:")
            print(f"  Price change: {(df['btc_price'].iloc[-1] / df['btc_price'].iloc[0] - 1) * 100:.2f}%")
            print(f"  Position correlation with price change: {btc_correlation:.3f}")
            print(f"  Average net position (USD): ${df['btc_net_position_usd'].mean():,.2f}")
            print(f"  Average net position (tokens): {df['btc_net_position_tokens'].mean():.4f} BTC")
            print(f"\nETH Analysis:")
            print(f"  Price change: {(df['eth_price'].iloc[-1] / df['eth_price'].iloc[0] - 1) * 100:.2f}%")
            print(f"  Position correlation with price change: {eth_correlation:.3f}")
            print(f"  Average net position (USD): ${df['eth_net_position_usd'].mean():,.2f}")
            print(f"  Average net position (tokens): {df['eth_net_position_tokens'].mean():.4f} ETH")
        
        plt.tight_layout()
        plt.savefig(f"backtest_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.show()
        
        # Save processed data
        df.to_csv(f"backtest_processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

async def main():
    backtest = HyperliquidBacktest()
    
    # Run backtest for 24 hours with 5-minute intervals
    # You can adjust these parameters
    import sys
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    await backtest.run_backtest(duration_hours=hours, interval_minutes=5)

if __name__ == "__main__":
    asyncio.run(main())