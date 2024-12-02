import { PythonShell } from 'python-shell';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { document } = req.body;

    let options = {
      mode: 'text',
      pythonPath: process.env.PYTHON_PATH, // This will now correctly handle the quoted path
      pythonOptions: ['-u'], // unbuffered stdout and stderr
      scriptPath: path.join(process.cwd(), 'backend', 'agents'),
      args: [JSON.stringify(document)]
    };

    try {
      const result = await new Promise((resolve, reject) => {
        PythonShell.run('document_enhancer.py', options, function (err, results) {
          if (err) reject(err);
          resolve(results[0]);
        });
      });

      const enhancedDocument = JSON.parse(result);
      res.status(200).json(enhancedDocument);
    } catch (error) {
      console.error('Error enhancing document:', error);
      res.status(500).json({ error: 'An error occurred while enhancing the document' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}