# Hyperliquid Tracker Dashboard

A real-time dashboard showing the top 100 Hyperliquid traders' positions and their correlation with BTC/ETH price movements.

## Features

### 📊 Time Series Chart
- Real-time BTC/ETH prices
- Net positions of top 100 traders in USD
- Interactive chart with dual Y-axes

### 📈 Net Positions Summary
- Aggregated long/short positions
- Current net positions in USD and tokens
- Number of active traders per asset

### 👥 Individual Trader Table
- Top 100 traders by all-time PNL
- Individual BTC/ETH positions
- Account values and performance metrics

## How It Works

### Data Collection Logic:
1. **Top 100 Selection**: Queries leaderboard API for top traders by all-time PNL
2. **Position Tracking**: Fetches each trader's BTC/ETH positions every 5 minutes
3. **Aggregation**: Sums all positions to calculate net market sentiment
4. **Correlation Analysis**: Compares position changes with price movements

### Update Frequency:
- **Positions**: Every 5 minutes
- **Leaderboard**: Every hour (to include new top performers)
- **Dashboard**: Real-time updates via API polling

## Deployment

### Environment Variables
```env
BACKEND_URL=http://your-digital-ocean-ip:8000
LEADERBOARD_URL=http://your-digital-ocean-ip:3000/leaderboard
```

### Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd dashboard
vercel

# Set environment variables in Vercel dashboard
# Then redeploy
vercel --prod
```

### Local Development
```bash
cd dashboard
npm install
npm run dev
```

Visit `http://localhost:3000`

## API Endpoints

### `/api/time-series`
Returns historical price and position data
```json
[
  {
    "timestamp": "2025-08-04T15:30:00.000Z",
    "btc_price": 114641,
    "eth_price": 3550,
    "btc_net_position_usd": 34117193,
    "eth_net_position_usd": -198014300,
    "btc_net_position_tokens": 297.6,
    "eth_net_position_tokens": -55769
  }
]
```

### `/api/net-positions`
Returns current aggregated positions
```json
[
  {
    "asset": "BTC",
    "long_usd": 85000000,
    "short_usd": 50000000,
    "net_usd": 35000000,
    "long_tokens": 742.5,
    "short_tokens": 437.2,
    "net_tokens": 305.3,
    "trader_count": 67
  }
]
```

### `/api/traders`
Returns individual trader data
```json
[
  {
    "ethAddress": "0x162cc7c861ebd0c06b3d72319201150482518185",
    "displayName": "Top Trader",
    "pnl_alltime": 1500000,
    "roi_alltime": 2.5,
    "account_value": 5000000,
    "btc_position": 5.2341,
    "eth_position": -150.7834,
    "btc_position_usd": 600000,
    "eth_position_usd": -535000
  }
]
```

## Architecture

```
Frontend (Vercel)     Backend (Digital Ocean)
├── Next.js App  ────► ├── Leaderboard API (Port 3000)
├── API Routes        ├── Backtest Script 
├── Real-time UI      └── PostgreSQL Database
└── Charts & Tables
```

## Tech Stack

- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Charts**: Recharts
- **Backend**: Python, Node.js (NestJS)
- **Database**: PostgreSQL (recommended for production)
- **Deployment**: Vercel (frontend), Digital Ocean (backend)

## Why This Would Be Popular

1. **Unique Data**: First public tracker of top trader positions
2. **Predictive Value**: Shows if successful traders predict market moves
3. **Real-time**: Updates every 5 minutes
4. **Visual**: Beautiful charts and easy-to-read tables
5. **Free**: Public access to premium trading insights

## Next Steps

1. **Connect to Real Data**: Update API endpoints to fetch from your Digital Ocean backend
2. **Add Database**: Store historical data in PostgreSQL
3. **Add Features**: 
   - Trader performance rankings
   - Position change alerts
   - Historical correlation analysis
   - Mobile responsive design
4. **SEO & Marketing**: Add metadata, social sharing, Twitter integration

This dashboard could become the go-to resource for tracking Hyperliquid's top traders!