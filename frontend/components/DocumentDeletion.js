import React, { useState, useEffect } from 'react';

const BACKEND_URL = 'http://localhost:8000';

export default function DocumentDeletion({ updateDocumentCount }) {
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/list_documents`);
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents);
      } else {
        console.error('Failed to fetch documents');
      }
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleCheckboxChange = (documentId) => {
    setSelectedDocuments(prev =>
      prev.includes(documentId)
        ? prev.filter(id => id !== documentId)
        : [...prev, documentId]
    );
  };

  const handleDelete = async () => {
    if (selectedDocuments.length === 0) return;

    try {
      const response = await fetch(`${BACKEND_URL}/delete_documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ documents: selectedDocuments }),
      });

      if (response.ok) {
        alert('Selected documents deleted successfully');
        fetchDocuments();
        setSelectedDocuments([]);
        updateDocumentCount();
      } else {
        alert('Failed to delete documents');
      }
    } catch (error) {
      console.error('Error deleting documents:', error);
      alert('An error occurred while deleting documents');
    }
  };

  return (
    <div>
      <h2>Delete Documents</h2>
      {documents.map((doc) => (
        <div key={doc.id}>
          <label>
            <input
              type="checkbox"
              checked={selectedDocuments.includes(doc.id)}
              onChange={() => handleCheckboxChange(doc.id)}
            />
            {doc.filename || doc.title || doc.id}
          </label>
        </div>
      ))}
      <button onClick={handleDelete} disabled={selectedDocuments.length === 0}>
        Delete Selected Documents
      </button>
    </div>
  );
}