import React, { useEffect } from 'react';

const DocumentList = ({ documents, updateDocumentCount, fetchIndexedDocuments }) => {
  useEffect(() => {
    fetchIndexedDocuments();
  }, [fetchIndexedDocuments]);

  const handleDelete = async (documentId) => {
    try {
      const response = await fetch('/api/deleteDocuments', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ documents: [documentId] }),
      });

      if (response.ok) {
        updateDocumentCount();
        fetchIndexedDocuments();
      } else {
        console.error('Failed to delete document');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  return (
    <div>
      <h2>Indexed Documents</h2>
      {documents.length === 0 ? (
        <p>No documents indexed yet.</p>
      ) : (
        <ul>
          {documents.map((doc) => (
            <li key={doc.id}>
              {doc.filename || doc.title || doc.id}
              <button onClick={() => handleDelete(doc.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentList;
