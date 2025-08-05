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
    
    const response = await fetch(`${apiServerUrl}/api/traders`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch traders from backend');
    }

    const traders = await response.json();
    
    res.status(200).json(traders);
  } catch (error) {
    console.error('Error fetching traders:', error);
    res.status(500).json({ error: 'Failed to fetch traders' });
  }
}