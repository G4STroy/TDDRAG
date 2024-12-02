import { PythonShell } from 'python-shell';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { action, ...params } = req.body;

    let options = {
      mode: 'text',
      pythonPath: process.env.PYTHON_PATH, // This will now correctly handle the quoted path
      pythonOptions: ['-u'], // unbuffered stdout and stderr
      scriptPath: path.join(process.cwd(), 'backend', 'agents'),
      args: [action, ...Object.values(params).map(JSON.stringify)]
    };

    try {
      const result = await new Promise((resolve, reject) => {
        PythonShell.run('indexing_agent.py', options, function (err, results) {
          if (err) reject(err);
          resolve(results[0]);
        });
      });

      const { result: indexingResult } = JSON.parse(result);
      res.status(200).json(indexingResult);
    } catch (error) {
      console.error('Error processing indexing action:', error);
      res.status(500).json({ error: 'An error occurred while processing the indexing action' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}