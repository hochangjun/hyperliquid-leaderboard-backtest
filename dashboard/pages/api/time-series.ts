import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Fetch data from your Digital Ocean backend
    const backendUrl = process.env.BACKEND_URL || 'YOUR_DIGITAL_OCEAN_IP';
    
    // For now, we'll fetch from a JSON file or database
    // In production, this would connect to your PostgreSQL database
    const response = await fetch(`${backendUrl}/api/time-series`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch time series data');
    }
    
    const data = await response.json();
    
    // Transform data if needed
    const transformedData = data.map((point: any) => ({
      timestamp: point.timestamp,
      btc_price: point.btc_price,
      eth_price: point.eth_price,
      btc_net_position_usd: point.btc_positions.net_usd,
      eth_net_position_usd: point.eth_positions.net_usd,
      btc_net_position_tokens: point.btc_positions.net_tokens,
      eth_net_position_tokens: point.eth_positions.net_tokens,
    }));

    res.status(200).json(transformedData);
  } catch (error) {
    console.error('Error fetching time series data:', error);
    
    // Return mock data for development
    const mockData = [
      {
        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
        btc_price: 114000,
        eth_price: 3500,
        btc_net_position_usd: 35000000,
        eth_net_position_usd: -195000000,
        btc_net_position_tokens: 307,
        eth_net_position_tokens: -55714,
      },
      {
        timestamp: new Date(Date.now() - 55 * 60 * 1000).toISOString(),
        btc_price: 114200,
        eth_price: 3510,
        btc_net_position_usd: 36000000,
        eth_net_position_usd: -194000000,
        btc_net_position_tokens: 315,
        eth_net_position_tokens: -55234,
      },
      {
        timestamp: new Date().toISOString(),
        btc_price: 114641,
        eth_price: 3550,
        btc_net_position_usd: 34117193,
        eth_net_position_usd: -198014300,
        btc_net_position_tokens: 297.6,
        eth_net_position_tokens: -55769,
      },
    ];
    
    res.status(200).json(mockData);
  }
}