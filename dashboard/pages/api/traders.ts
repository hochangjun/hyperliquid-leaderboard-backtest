import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // This would fetch from your leaderboard API and combine with position data
    const leaderboardUrl = process.env.LEADERBOARD_URL || 'http://YOUR_DIGITAL_OCEAN_IP:3000/leaderboard';
    
    // Fetch top 100 traders
    const leaderboardResponse = await fetch(leaderboardUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ limit: 100 })
    });

    if (!leaderboardResponse.ok) {
      throw new Error('Failed to fetch leaderboard');
    }

    const leaderboardData = await leaderboardResponse.json();
    
    // For each trader, you'd fetch their current positions
    // This is a simplified version - in production you'd batch these requests
    const tradersWithPositions = leaderboardData.leaderboardRows.map((trader: any, index: number) => {
      const allTimePerf = trader.windowPerformances.find((w: any) => w[0] === 'allTime');
      
      return {
        ethAddress: trader.ethAddress,
        displayName: trader.displayName || null,
        pnl_alltime: parseFloat(allTimePerf?.[1]?.pnl || '0'),
        roi_alltime: parseFloat(allTimePerf?.[1]?.roi || '0'),
        account_value: parseFloat(trader.accountValue),
        // These would be fetched from position data in production
        btc_position: Math.random() * 10 - 5, // Mock data
        eth_position: Math.random() * 100 - 50, // Mock data
        btc_position_usd: (Math.random() * 10 - 5) * 114000,
        eth_position_usd: (Math.random() * 100 - 50) * 3500,
      };
    });

    res.status(200).json(tradersWithPositions);
  } catch (error) {
    console.error('Error fetching traders:', error);
    
    // Return mock data for development
    const mockTraders = Array.from({ length: 100 }, (_, i) => ({
      ethAddress: `0x${Math.random().toString(16).substr(2, 40)}`,
      displayName: i < 10 ? `Trader ${i + 1}` : null,
      pnl_alltime: Math.random() * 1000000 + 100000,
      roi_alltime: Math.random() * 5 + 0.5,
      account_value: Math.random() * 5000000 + 500000,
      btc_position: Math.random() * 10 - 5,
      eth_position: Math.random() * 100 - 50,
      btc_position_usd: (Math.random() * 10 - 5) * 114000,
      eth_position_usd: (Math.random() * 100 - 50) * 3500,
    }));
    
    res.status(200).json(mockTraders);
  }
}