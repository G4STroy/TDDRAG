import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export default async function handler(req, res) {
  try {
    const { stdout, stderr } = await execAsync('python backend/agents/indexing_agent.py list');
    if (stderr) {
      console.error('Python script error:', stderr);
      throw new Error(stderr);
    }
    const result = JSON.parse(stdout);
    res.status(200).json({ documents: result.result });
  } catch (error) {
    console.error('Error in listDocuments:', error);
    res.status(500).json({ error: error.message });
  }
}