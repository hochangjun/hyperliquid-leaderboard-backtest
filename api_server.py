from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import glob
import os
from datetime import datetime, timedelta
import requests
import asyncio
import aiohttp

app = Flask(__name__)
CORS(app)  # Enable CORS for Vercel frontend

def get_latest_data():
    """Get the most recent backtest data"""
    try:
        data_files = sorted(glob.glob("backtest_data_*.json"))
        if not data_files:
            return []
        
        with open(data_files[-1], 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

@app.route('/api/time-series', methods=['GET'])
def get_time_series():
    """Get historical time series data for the dashboard"""
    try:
        # Get query parameters
        hours = request.args.get('hours', '24')  # Default to last 24 hours
        hours = int(hours)
        
        data = get_latest_data()
        
        # Filter to last N hours
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_data = []
        for point in data:
            try:
                timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
                if timestamp >= cutoff_time:
                    filtered_data.append({
                        'timestamp': point['timestamp'],
                        'btc_price': point['btc_price'],
                        'eth_price': point['eth_price'],
                        'btc_net_position_usd': point['btc_positions']['net_usd'],
                        'eth_net_position_usd': point['eth_positions']['net_usd'],
                        'btc_net_position_tokens': point['btc_positions']['net_tokens'],
                        'eth_net_position_tokens': point['eth_positions']['net_tokens'],
                    })
            except Exception as e:
                continue
                
        return jsonify(filtered_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/net-positions', methods=['GET'])
def get_net_positions():
    """Get current net positions summary"""
    try:
        data = get_latest_data()
        if not data:
            return jsonify([])
        
        # Get the most recent data point
        latest = data[-1]
        
        result = [
            {
                'asset': 'BTC',
                'long_usd': latest['btc_positions']['long_usd'],
                'short_usd': latest['btc_positions']['short_usd'],
                'net_usd': latest['btc_positions']['net_usd'],
                'long_tokens': latest['btc_positions']['long_tokens'],
                'short_tokens': latest['btc_positions']['short_tokens'],
                'net_tokens': latest['btc_positions']['net_tokens'],
                'trader_count': latest['btc_positions']['count']
            },
            {
                'asset': 'ETH',
                'long_usd': latest['eth_positions']['long_usd'],
                'short_usd': latest['eth_positions']['short_usd'],
                'net_usd': latest['eth_positions']['net_usd'],
                'long_tokens': latest['eth_positions']['long_tokens'],
                'short_tokens': latest['eth_positions']['short_tokens'],
                'net_tokens': latest['eth_positions']['net_tokens'],
                'trader_count': latest['eth_positions']['count']
            }
        ]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traders', methods=['GET'])
def get_traders():
    """Get individual trader data with positions"""
    try:
        # Get leaderboard data
        leaderboard_response = requests.post(
            "http://localhost:3000/leaderboard",
            json={"limit": 100}
        )
        
        if not leaderboard_response.ok:
            return jsonify({'error': 'Failed to fetch leaderboard'}), 500
        
        leaderboard_data = leaderboard_response.json()
        
        # Get latest data point to extract trader positions
        data = get_latest_data()
        latest_positions = {}
        if data and 'trader_positions' in data[-1]:
            latest_positions = data[-1]['trader_positions']
        
        traders = []
        
        # Filter for traders with positive all-time PNL only
        for trader in leaderboard_data.get('leaderboardRows', []):
            alltime_stats = next((w[1] for w in trader['windowPerformances'] if w[0] == 'allTime'), {})
            pnl_alltime = float(alltime_stats.get('pnl', 0))
            
            # Only include traders with positive PNL
            if pnl_alltime > 0:
                eth_address = trader['ethAddress']
                
                # Get position data if available
                position_data = latest_positions.get(eth_address, {})
                btc_position = position_data.get('BTC@PERP', {})
                eth_position = position_data.get('ETH@PERP', {})
                
                traders.append({
                    'ethAddress': eth_address,
                    'displayName': trader.get('displayName'),
                    'pnl_alltime': pnl_alltime,
                    'roi_alltime': float(alltime_stats.get('roi', 0)),
                    'account_value': float(trader.get('accountValue', 0)),
                    'btc_position': btc_position.get('szi', 0) if btc_position else 0,
                    'eth_position': eth_position.get('szi', 0) if eth_position else 0,
                    'btc_position_usd': btc_position.get('position_value_usd', 0) if btc_position else 0,
                    'eth_position_usd': eth_position.get('position_value_usd', 0) if eth_position else 0,
                })
        
        return jsonify(traders)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-data', methods=['GET'])
def get_current_data():
    """Get the most recent data point"""
    try:
        data = get_latest_data()
        if not data:
            return jsonify({'error': 'No data available'}), 404
        
        return jsonify(data[-1])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        data = get_latest_data()
        return jsonify({
            'status': 'healthy',
            'data_points': len(data),
            'last_update': data[-1]['timestamp'] if data else None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)