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
        
    async def get_top_traders(self, limit: int = 100) -> List[str]:
        """Get top 100 traders by PNL from the leaderboard"""
        payload = {
            "limit": limit,
            "offset": 0,
            "sort": {
                "timePeriod": "allTime",
                "type": "pnl",
                "direction": "desc"
            }
        }
        
        try:
            response = requests.post(self.leaderboard_api, json=payload)
            data = response.json()
            
            if "error" in data:
                print(f"Error fetching leaderboard: {data['error']}")
                return []
            
            traders = [row["ethAddress"] for row in data["leaderboardRows"]]
            print(f"Fetched {len(traders)} top traders")
            return traders[:limit]
        except Exception as e:
            print(f"Error connecting to leaderboard API: {e}")
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
    
    def aggregate_positions(self, positions: List[Dict]) -> Dict[str, Dict]:
        """Aggregate positions by asset (BTC, ETH)"""
        aggregated = defaultdict(lambda: {"long": 0, "short": 0, "net": 0, "count": 0})
        
        for trader_data in positions:
            for position in trader_data["positions"]:
                asset = position["position"]["coin"]
                if asset in ["BTC", "ETH"]:
                    size = float(position["position"]["szi"])
                    if size > 0:
                        aggregated[asset]["long"] += size
                    else:
                        aggregated[asset]["short"] += abs(size)
                    aggregated[asset]["net"] += size
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
            
            for asset in data[0]["universe"]:
                if asset["name"] == coin:
                    ctx_idx = asset["szDecimals"]
                    # Find the corresponding asset context
                    for i, ctx in enumerate(data[1]):
                        if i == ctx_idx:
                            return float(ctx["markPx"])
            return 0.0
        except Exception as e:
            print(f"Error fetching price for {coin}: {e}")
            return 0.0
    
    async def collect_data_point(self, traders: List[str]) -> Dict:
        """Collect one data point: positions and prices"""
        # Get all positions
        positions = await self.get_all_positions(traders)
        aggregated = self.aggregate_positions(positions)
        
        # Get prices
        btc_price = await self.get_price_data("BTC")
        eth_price = await self.get_price_data("ETH")
        
        data_point = {
            "timestamp": datetime.now(),
            "btc_price": btc_price,
            "eth_price": eth_price,
            "btc_positions": aggregated.get("BTC", {"long": 0, "short": 0, "net": 0, "count": 0}),
            "eth_positions": aggregated.get("ETH", {"long": 0, "short": 0, "net": 0, "count": 0})
        }
        
        return data_point
    
    async def run_backtest(self, duration_hours: int = 24, interval_minutes: int = 5):
        """Run the backtest for specified duration"""
        print(f"Starting backtest for {duration_hours} hours with {interval_minutes} minute intervals")
        
        # Get top traders
        traders = await self.get_top_traders(100)
        if not traders:
            print("Failed to get traders. Make sure the leaderboard API is running.")
            return
        
        # Calculate number of iterations
        iterations = (duration_hours * 60) // interval_minutes
        
        # Load existing data if any
        data_points = self.load_existing_data()
        
        for i in range(iterations):
            print(f"\nCollecting data point {i+1}/{iterations}")
            
            try:
                data_point = await self.collect_data_point(traders)
                data_points.append(data_point)
                
                # Print current status
                print(f"Timestamp: {data_point['timestamp']}")
                print(f"BTC Price: ${data_point['btc_price']:,.2f}")
                print(f"BTC Net Position: {data_point['btc_positions']['net']:.4f}")
                print(f"ETH Price: ${data_point['eth_price']:,.2f}")
                print(f"ETH Net Position: {data_point['eth_positions']['net']:.4f}")
                
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
                'btc_net_position': dp['btc_positions']['net'],
                'eth_net_position': dp['eth_positions']['net'],
                'btc_long': dp['btc_positions']['long'],
                'btc_short': dp['btc_positions']['short'],
                'eth_long': dp['eth_positions']['long'],
                'eth_short': dp['eth_positions']['short']
            })
        
        df = pd.DataFrame(df_data)
        df.set_index('timestamp', inplace=True)
        
        # Calculate price changes
        df['btc_price_change'] = df['btc_price'].pct_change()
        df['eth_price_change'] = df['eth_price'].pct_change()
        
        # Calculate position changes
        df['btc_position_change'] = df['btc_net_position'].diff()
        df['eth_position_change'] = df['eth_net_position'].diff()
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # BTC Analysis
        ax1 = axes[0, 0]
        ax1_twin = ax1.twinx()
        ax1.plot(df.index, df['btc_price'], 'b-', label='BTC Price')
        ax1_twin.plot(df.index, df['btc_net_position'], 'r-', label='Net Position')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('BTC Price ($)', color='b')
        ax1_twin.set_ylabel('Net Position', color='r')
        ax1.set_title('BTC Price vs Top 100 Traders Net Position')
        ax1.tick_params(axis='y', labelcolor='b')
        ax1_twin.tick_params(axis='y', labelcolor='r')
        
        # ETH Analysis
        ax2 = axes[0, 1]
        ax2_twin = ax2.twinx()
        ax2.plot(df.index, df['eth_price'], 'b-', label='ETH Price')
        ax2_twin.plot(df.index, df['eth_net_position'], 'r-', label='Net Position')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('ETH Price ($)', color='b')
        ax2_twin.set_ylabel('Net Position', color='r')
        ax2.set_title('ETH Price vs Top 100 Traders Net Position')
        ax2.tick_params(axis='y', labelcolor='b')
        ax2_twin.tick_params(axis='y', labelcolor='r')
        
        # Correlation Analysis
        # Remove NaN values for correlation calculation
        btc_corr_data = df[['btc_price_change', 'btc_position_change']].dropna()
        eth_corr_data = df[['eth_price_change', 'eth_position_change']].dropna()
        
        if len(btc_corr_data) > 2:
            btc_correlation = btc_corr_data.corr().iloc[0, 1]
            eth_correlation = eth_corr_data.corr().iloc[0, 1]
            
            # Scatter plots
            ax3 = axes[1, 0]
            ax3.scatter(btc_corr_data['btc_position_change'], btc_corr_data['btc_price_change'])
            ax3.set_xlabel('Position Change')
            ax3.set_ylabel('Price Change %')
            ax3.set_title(f'BTC Position Change vs Price Change\nCorrelation: {btc_correlation:.3f}')
            
            ax4 = axes[1, 1]
            ax4.scatter(eth_corr_data['eth_position_change'], eth_corr_data['eth_price_change'])
            ax4.set_xlabel('Position Change')
            ax4.set_ylabel('Price Change %')
            ax4.set_title(f'ETH Position Change vs Price Change\nCorrelation: {eth_correlation:.3f}')
            
            # Print summary statistics
            print("\n=== BACKTEST RESULTS ===")
            print(f"Data points collected: {len(df)}")
            print(f"Duration: {df.index[-1] - df.index[0]}")
            print(f"\nBTC Analysis:")
            print(f"  Price change: {(df['btc_price'].iloc[-1] / df['btc_price'].iloc[0] - 1) * 100:.2f}%")
            print(f"  Position correlation with price change: {btc_correlation:.3f}")
            print(f"  Average net position: {df['btc_net_position'].mean():.4f}")
            print(f"\nETH Analysis:")
            print(f"  Price change: {(df['eth_price'].iloc[-1] / df['eth_price'].iloc[0] - 1) * 100:.2f}%")
            print(f"  Position correlation with price change: {eth_correlation:.3f}")
            print(f"  Average net position: {df['eth_net_position'].mean():.4f}")
        
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