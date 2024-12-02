import { PythonShell } from 'python-shell';
import path from 'path';
import formidable from 'formidable';
import fs from 'fs';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const form = new formidable.IncomingForm();
    form.parse(req, async (err, fields, files) => {
      if (err) {
        console.error('Error parsing form:', err);
        return res.status(500).json({ error: 'Error processing file upload' });
      }

      const { action } = fields;
      const file = files.file;

      let options = {
        mode: 'text',
        pythonPath: process.env.PYTHON_PATH,
        pythonOptions: ['-u'],
        scriptPath: path.join(process.cwd(), 'backend', 'agents'),
        args: [action, file.name, fs.readFileSync(file.path, 'utf8')],
        env: {
          ...process.env,
          PYTHONPATH: path.join(process.cwd(), 'backend')
        }
      };

      try {
        const result = await new Promise((resolve, reject) => {
          PythonShell.run('document_processing.py', options, function (err, results) {
            if (err) reject(err);
            resolve(results[0]);
          });
        });

        const { success, message } = JSON.parse(result);
        if (success) {
          res.status(200).json({ message });
        } else {
          res.status(500).json({ error: message });
        }
      } catch (error) {
        console.error('Error processing document:', error);
        res.status(500).json({ error: 'An error occurred while processing the document' });
      }
    });
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}