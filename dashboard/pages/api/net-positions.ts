import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Fetch from your backend
    const backendUrl = process.env.BACKEND_URL;
    
    if (!backendUrl) {
      throw new Error('BACKEND_URL not configured');
    }
    
    const response = await fetch(`${backendUrl}/api/net-positions`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch net positions');
    }
    
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    console.error('Error fetching net positions:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}