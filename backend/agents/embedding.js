import { PythonShell } from 'python-shell';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { text } = req.body;

    let options = {
      mode: 'text',
      pythonPath: process.env.PYTHON_PATH, // This will now correctly handle the quoted path
      pythonOptions: ['-u'], // unbuffered stdout and stderr
      scriptPath: path.join(process.cwd(), 'backend', 'agents'),
      args: [text]
    };

    try {
      const result = await new Promise((resolve, reject) => {
        PythonShell.run('embedding_agent.py', options, function (err, results) {
          if (err) reject(err);
          resolve(results[0]);
        });
      });

      const { embedding } = JSON.parse(result);
      res.status(200).json({ embedding });
    } catch (error) {
      console.error('Error generating embedding:', error);
      res.status(500).json({ error: 'An error occurred while generating the embedding' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}