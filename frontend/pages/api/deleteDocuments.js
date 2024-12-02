import axios from 'axios';

export default async function handler(req, res) {
  if (req.method === 'DELETE') {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.post(`${backendUrl}/delete_documents`, req.body);
      res.status(response.data.success ? 200 : 400).json(response.data);
    } catch (error) {
      console.error('Error deleting documents:', error);
      res.status(500).json({ success: false, message: error.message });
    }
  } else {
    res.setHeader('Allow', ['DELETE']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}