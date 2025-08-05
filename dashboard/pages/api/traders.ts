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
    const apiServerUrl = process.env.API_SERVER_URL;
    
    if (!apiServerUrl || apiServerUrl.includes('YOUR_DIGITAL_OCEAN_IP')) {
      console.log('API_SERVER_URL not configured properly');
      // Return empty array to prevent frontend crash
      return res.status(200).json([]);
    }
    
    const response = await fetch(`${apiServerUrl}/api/traders`);
    
    if (!response.ok) {
      console.error('Backend returned error:', response.status, response.statusText);
      return res.status(200).json([]); // Return empty array instead of error
    }

    const traders = await response.json();
    
    res.status(200).json(traders);
  } catch (error) {
    console.error('Error fetching traders:', error);
    // Return empty array to prevent frontend crash
    res.status(200).json([]);
  }
}