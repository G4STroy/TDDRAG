import { useState } from 'react';

const BACKEND_URL = 'http://localhost:8000'; // Adjust this if needed

export default function DocumentUpload({ updateDocumentCount }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('Document uploaded and indexed successfully!');
          setFile(null);
          await updateDocumentCount();
        } else {
          alert(`Failed to upload document: ${result.message || 'Unknown error'}`);
        }
      } else {
        const errorData = await response.json();
        alert(`Failed to upload document: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('An error occurred while uploading the document.');
    }

    setUploading(false);
  };

  return (
    <div>
      <h2>Upload and Index Documents</h2>
      <input type="file" onChange={handleFileChange} accept=".txt,.pdf,.doc,.docx" />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload and Index'}
      </button>
    </div>
  );
}