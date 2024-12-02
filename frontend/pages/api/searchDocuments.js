import axios from 'axios';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { query, searchType } = req.body;

    try {
      const response = await axios.post('http://localhost:5000/search_documents', {
        query,
        searchType
      });

      res.status(200).json(response.data);
    } catch (error) {
      console.error('Error processing query:', error);
      res.status(500).json({ error: 'Error processing query' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
