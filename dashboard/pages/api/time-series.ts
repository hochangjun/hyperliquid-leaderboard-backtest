import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Proxy to your backend API server
    const apiServerUrl = process.env.API_SERVER_URL || 'http://YOUR_DIGITAL_OCEAN_IP:8000';
    const hours = req.query.hours || '24';
    
    const response = await fetch(`${apiServerUrl}/api/time-series?hours=${hours}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch time series from backend');
    }

    const data = await response.json();
    
    res.status(200).json(data);
  } catch (error) {
    console.error('Error fetching time series:', error);
    res.status(500).json({ error: 'Failed to fetch time series data' });
  }
}