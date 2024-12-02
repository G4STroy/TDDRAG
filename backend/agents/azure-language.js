import { PythonShell } from 'python-shell';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { action, text } = req.body;

    let options = {
      mode: 'text',
      pythonPath: process.env.PYTHON_PATH,
      pythonOptions: ['-u'],
      scriptPath: path.join(process.cwd(), 'backend', 'agents'),
      args: [action, text]
    };

    try {
      const result = await new Promise((resolve, reject) => {
        PythonShell.run('azure_language_service.py', options, function (err, results) {
          if (err) reject(err);
          resolve(results[0]);
        });
      });

      const parsedResult = JSON.parse(result);
      res.status(200).json(parsedResult);
    } catch (error) {
      console.error('Error processing Azure Language Service request:', error);
      res.status(500).json({ error: 'An error occurred while processing the request' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}