import path from 'path';
import formidable from 'formidable';
import { spawn } from 'child_process';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const form = formidable({});
    form.parse(req, async (err, fields, files) => {
      if (err) {
        console.error('Error parsing form:', err);
        return res.status(500).json({ error: 'Error processing file upload' });
      }

      const file = files.file && files.file[0];

      if (!file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      console.log('File object:', file);

      let options = {
        mode: 'text',
        pythonPath: decodeURIComponent(process.env.PYTHON_PATH),
        pythonOptions: ['-u'],
        scriptPath: path.join(process.cwd(), '..', 'backend', 'agents'),
        args: ['upload', file.originalFilename, file.filepath]
      };

      console.log('Python Path:', options.pythonPath);
      console.log('Script Path:', options.scriptPath);
      console.log('Arguments:', options.args);

      try {
        const pythonProcess = spawn(options.pythonPath, [
          path.join(options.scriptPath, 'document_processing.py'),
          'upload',
          file.originalFilename,
          file.filepath
        ]);

        let pythonOutput = '';
        let pythonError = '';

        pythonProcess.stdout.on('data', (data) => {
          const output = data.toString();
          console.log(`Python stdout: ${output}`);
          pythonOutput += output;
        });

        pythonProcess.stderr.on('data', (data) => {
          const error = data.toString();
          console.error(`Python stderr: ${error}`);
          pythonError += error;
        });

        pythonProcess.on('close', (code) => {
          console.log(`Python process exited with code ${code}`);
          console.log('Full Python output:', pythonOutput);

          if (code === 0) {
            try {
              const jsonMatch = pythonOutput.match(/OUTPUT_START(.*)OUTPUT_END/s);
              if (jsonMatch) {
                const jsonString = jsonMatch[1].trim();
                const result = JSON.parse(jsonString);
                res.status(200).json(result);
              } else {
                throw new Error('No valid JSON output found');
              }
            } catch (error) {
              console.error('Error parsing Python output:', error);
              res.status(500).json({ error: 'Error processing document', details: error.message });
            }
          } else {
            res.status(500).json({ error: 'Python process error', code });
          }
        });
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

console.log('PYTHON_PATH:', process.env.PYTHON_PATH);












