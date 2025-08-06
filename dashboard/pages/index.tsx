import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface DataPoint {
  timestamp: string;
  btc_price: number;
  eth_price: number;
  btc_net_position_usd: number;
  eth_net_position_usd: number;
  btc_net_position_tokens: number;
  eth_net_position_tokens: number;
}

interface Trader {
  ethAddress: string;
  pnl_alltime: number;
  roi_alltime: number;
  account_value: number;
  btc_position?: number;
  eth_position?: number;
  btc_position_usd?: number;
  eth_position_usd?: number;
}

interface NetPosition {
  asset: string;
  long_usd: number;
  short_usd: number;
  net_usd: number;
  long_tokens: number;
  short_tokens: number;
  net_tokens: number;
  trader_count: number;
}

export default function Dashboard() {
  const [timeSeriesData, setTimeSeriesData] = useState<DataPoint[]>([]);
  const [netPositions, setNetPositions] = useState<NetPosition[]>([]);
  const [traders, setTraders] = useState<Trader[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000); // Update every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [timeSeriesRes, netPositionsRes, tradersRes] = await Promise.all([
        fetch('/api/time-series'),
        fetch('/api/net-positions'),
        fetch('/api/traders')
      ]);

      const timeSeries = await timeSeriesRes.json();
      const netPos = await netPositionsRes.json();
      const tradersData = await tradersRes.json();

      setTimeSeriesData(timeSeries);
      setNetPositions(netPos);
      setTraders(tradersData);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatMillion = (value: number) => {
    return `$${(value / 1_000_000).toFixed(1)}M`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-2xl">Loading Hyperliquid Tracker...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-2">Hyperliquid Top 100 Trader Tracker</h1>
          <p className="text-gray-400">
            Real-time positions of top 100 PNL traders on Hyperliquid
          </p>
          {lastUpdate && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {format(lastUpdate, 'MMM dd, yyyy HH:mm:ss')}
            </p>
          )}
        </div>

        {/* Time Series Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* BTC Chart */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">BTC: Price vs Net Positions</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => format(new Date(value), 'MM/dd HH:mm')}
                    stroke="#9CA3AF"
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis 
                    yAxisId="price" 
                    orientation="left" 
                    stroke="#F59E0B"
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    domain={['dataMin - 1000', 'dataMax + 1000']}
                    width={65}
                  />
                  <YAxis 
                    yAxisId="position" 
                    orientation="right" 
                    stroke="#10B981"
                    tickFormatter={(value) => `$${(value / 1_000_000).toFixed(0)}M`}
                    width={65}
                  />
                  <Tooltip 
                    labelFormatter={(value) => format(new Date(value), 'MMM dd, HH:mm')}
                    formatter={(value: any, name: string) => {
                      if (name.includes('BTC Price')) return [formatCurrency(value), name];
                      return [formatMillion(value), name];
                    }}
                  />
                  <Legend />
                  <Line 
                    yAxisId="price" 
                    type="monotone" 
                    dataKey="btc_price" 
                    stroke="#F59E0B" 
                    name="BTC Price"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line 
                    yAxisId="position" 
                    type="monotone" 
                    dataKey="btc_net_position_usd" 
                    stroke="#10B981" 
                    name="BTC Net Position"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* ETH Chart */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">ETH: Price vs Net Positions</h2>
            <div className="h-96">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timeSeriesData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(value) => format(new Date(value), 'MM/dd HH:mm')}
                    stroke="#9CA3AF"
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis 
                    yAxisId="price" 
                    orientation="left" 
                    stroke="#3B82F6"
                    tickFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
                    domain={['dataMin - 100', 'dataMax + 100']}
                    width={65}
                  />
                  <YAxis 
                    yAxisId="position" 
                    orientation="right" 
                    stroke="#EF4444"
                    tickFormatter={(value) => `$${(value / 1_000_000).toFixed(0)}M`}
                    width={65}
                  />
                  <Tooltip 
                    labelFormatter={(value) => format(new Date(value), 'MMM dd, HH:mm')}
                    formatter={(value: any, name: string) => {
                      if (name.includes('ETH Price')) return [formatCurrency(value), name];
                      return [formatMillion(value), name];
                    }}
                  />
                  <Legend />
                  <Line 
                    yAxisId="price" 
                    type="monotone" 
                    dataKey="eth_price" 
                    stroke="#3B82F6" 
                    name="ETH Price"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line 
                    yAxisId="position" 
                    type="monotone" 
                    dataKey="eth_net_position_usd" 
                    stroke="#EF4444" 
                    name="ETH Net Position"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Net Positions Summary */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Current Net Positions Summary</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-600">
                  <th className="text-left p-3">Asset</th>
                  <th className="text-right p-3">Long (USD)</th>
                  <th className="text-right p-3">Short (USD)</th>
                  <th className="text-right p-3">Net (USD)</th>
                  <th className="text-right p-3">Net (Tokens)</th>
                  <th className="text-right p-3">Traders</th>
                </tr>
              </thead>
              <tbody>
                {netPositions.map((pos) => (
                  <tr key={pos.asset} className="border-b border-gray-700">
                    <td className="p-3 font-semibold">{pos.asset}</td>
                    <td className="p-3 text-right text-green-400">{formatMillion(pos.long_usd)}</td>
                    <td className="p-3 text-right text-red-400">{formatMillion(pos.short_usd)}</td>
                    <td className={`p-3 text-right font-semibold ${pos.net_usd >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {formatMillion(pos.net_usd)}
                    </td>
                    <td className="p-3 text-right">
                      {pos.net_tokens.toFixed(4)} {pos.asset}
                    </td>
                    <td className="p-3 text-right">{pos.trader_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Individual Traders Table */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Top 100 Traders Individual Positions</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-600">
                  <th className="text-left p-3">Trader</th>
                  <th className="text-right p-3">All-time PNL</th>
                  <th className="text-right p-3">Account Value</th>
                  <th className="text-right p-3">BTC Position</th>
                  <th className="text-right p-3">BTC (USD)</th>
                  <th className="text-right p-3">ETH Position</th>
                  <th className="text-right p-3">ETH (USD)</th>
                </tr>
              </thead>
              <tbody>
                {traders.slice(0, 50).map((trader, index) => ( // Show first 50, add pagination later
                  <tr key={trader.ethAddress} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-3">
                      <div className="flex items-center">
                        <span className="text-gray-400 mr-2">#{index + 1}</span>
                        <span className="font-mono text-xs">
                          {trader.ethAddress.slice(0, 8)}...{trader.ethAddress.slice(-6)}
                        </span>
                      </div>
                    </td>
                    <td className="p-3 text-right font-semibold text-green-400">
                      {formatCurrency(trader.pnl_alltime)}
                    </td>
                    <td className="p-3 text-right">
                      {formatCurrency(trader.account_value)}
                    </td>
                    <td className="p-3 text-right">
                      {trader.btc_position ? trader.btc_position.toFixed(4) : '0.0000'}
                    </td>
                    <td className="p-3 text-right">
                      {trader.btc_position_usd ? formatCurrency(trader.btc_position_usd) : '$0'}
                    </td>
                    <td className="p-3 text-right">
                      {trader.eth_position ? trader.eth_position.toFixed(4) : '0.0000'}
                    </td>
                    <td className="p-3 text-right">
                      {trader.eth_position_usd ? formatCurrency(trader.eth_position_usd) : '$0'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}