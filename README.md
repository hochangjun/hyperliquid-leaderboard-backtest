# Hyperliquid Leaderboard Backtest

A backtesting system that analyzes whether the top 100 PNL traders on Hyperliquid accurately predict BTC and ETH price movements based on their position directions.

## Overview

This project:
- Queries the top 100 traders by PNL from Hyperliquid
- Tracks their BTC/ETH positions (long/short) over time
- Compares position changes with actual price movements
- Calculates accuracy metrics and correlations
- Generates visualizations of trader positioning vs market movements

## Features

- **Real-time data collection**: Queries positions every 5 minutes
- **Automatic recovery**: Resumes from crashes with checkpoint system
- **Incremental saves**: Data saved hourly to prevent loss
- **Correlation analysis**: Measures how position changes predict price movements
- **Visualization**: Time series plots and correlation charts
- **Production ready**: Includes systemd services and deployment scripts

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for the leaderboard API)

### Local Setup

1. **Clone the repository:**
```bash
git clone https://github.com/hochangjun/hyperliquid-leaderboard-backtest.git
cd hyperliquid-leaderboard-backtest
```

2. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Start the leaderboard API:**
```bash
cd hyperliquid-leaderboard
npm install
npm start
```

4. **Run the backtest (in another terminal):**
```bash
source venv/bin/activate
python backtest.py 24  # Run for 24 hours
```

## How It Works

1. **Data Collection**: 
   - Fetches top 100 traders from cached leaderboard API
   - Queries each trader's positions from Hyperliquid API
   - Records BTC/ETH prices from Hyperliquid
   - Saves checkpoint every hour

2. **Analysis**:
   - Calculates net positions (long - short) for all traders
   - Measures correlation between position changes and price movements
   - Determines accuracy of directional predictions

3. **Output**:
   - `backtest_data_*.json`: Raw collected data
   - `backtest_processed_*.csv`: Processed time series data
   - `backtest_analysis_*.png`: Visualization charts

## Deployment

See [deploy/README.md](deploy/README.md) for Digital Ocean deployment instructions.

## Data Collection Schedule

- **Every 5 minutes**: New data point collected
- **Every hour**: Checkpoint saved to disk
- **On crash**: Automatically resumes from last checkpoint

## Project Structure

```
.
├── backtest.py              # Main backtest script
├── quick_test.py            # Test script to verify setup
├── requirements.txt         # Python dependencies
├── hyperliquid-leaderboard/ # Caching API service
└── deploy/                  # Deployment scripts
    ├── setup.sh
    ├── backup.sh
    └── systemd/            # Service files
```

## Configuration

Modify parameters in `backtest.py`:
- `duration_hours`: Total collection time (default: 24)
- `interval_minutes`: Data collection frequency (default: 5)

## License

MIT