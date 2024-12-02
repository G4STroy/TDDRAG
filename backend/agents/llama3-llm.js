import { PythonShell } from 'python-shell';
import path from 'path';

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { action, prompt, messages, max_tokens } = req.body;

    let options = {
      mode: 'text',
      pythonPath: process.env.PYTHON_PATH, // This will now correctly handle the quoted path
      pythonOptions: ['-u'], // unbuffered stdout and stderr
      scriptPath: path.join(process.cwd(), 'backend', 'agents'),
      args: [action, JSON.stringify(prompt || messages), max_tokens?.toString()]
    };

    try {
      const result = await new Promise((resolve, reject) => {
        PythonShell.run('llama3_llm.py', options, function (err, results) {
          if (err) reject(err);
          resolve(results[0]);
        });
      });

      const { result: llmResponse } = JSON.parse(result);
      res.status(200).json({ response: llmResponse });
    } catch (error) {
      console.error('Error processing LLM request:', error);
      res.status(500).json({ error: 'An error occurred while processing the LLM request' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}