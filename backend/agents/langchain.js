import { PythonShell } from 'python-shell';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { query, searchType } = req.body;

    let options = {
      mode: 'text',
      pythonPath: process.env.PYTHON_PATH, // This will now correctly handle the quoted path
      pythonOptions: ['-u'], // unbuffered stdout and stderr
      scriptPath: path.join(process.cwd(), 'backend', 'agents'),
      args: [query, searchType]
    };

    try {
      const result = await new Promise((resolve, reject) => {
        PythonShell.run('langchain_integration.py', options, function (err, results) {
          if (err) reject(err);
          resolve(results[0]);
        });
      });

      const { search_results, llm_response } = JSON.parse(result);
      res.status(200).json({ searchResults: search_results, llmResponse: llm_response });
    } catch (error) {
      console.error('Error processing query:', error);
      res.status(500).json({ error: 'An error occurred while processing the query' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}