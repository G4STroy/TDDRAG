// pages/api/documentCount.js
import { IndexingAgent } from '../../backend/agents/indexing_agent';

export default async function handler(req, res) {
  console.log('Document count API route hit');
  if (req.method === 'GET') {
    try {
      console.log('Attempting to fetch document count');
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      console.log('Backend URL:', backendUrl);
      const response = await fetch(`${backendUrl}/document_count`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Document count response:', data);
      res.status(200).json({ count: data.count });
    } catch (error) {
      console.error('Error fetching document count:', error);
      res.status(500).json({ error: 'Failed to fetch document count' });
    }
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}