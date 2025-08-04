import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // This would fetch from your backend or database
    const backendUrl = process.env.BACKEND_URL || 'YOUR_DIGITAL_OCEAN_IP';
    
    // For now, return current net positions
    const mockData = [
      {
        asset: 'BTC',
        long_usd: 85000000,
        short_usd: 50000000,
        net_usd: 35000000,
        long_tokens: 742.5,
        short_tokens: 437.2,
        net_tokens: 305.3,
        trader_count: 67
      },
      {
        asset: 'ETH',
        long_usd: 45000000,
        short_usd: 240000000,
        net_usd: -195000000,
        long_tokens: 12676,
        short_tokens: 67589,
        net_tokens: -54913,
        trader_count: 89
      }
    ];

    res.status(200).json(mockData);
  } catch (error) {
    console.error('Error fetching net positions:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}