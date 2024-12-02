import React, { useState, useEffect } from 'react';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';
import SearchInterface from './SearchInterface';

const BACKEND_URL = 'http://localhost:8000';

function App() {
  const [documentCount, setDocumentCount] = useState(0);

  const updateDocumentCount = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/document_count`);
      if (response.ok) {
        const data = await response.json();
        setDocumentCount(data.count);
      } else {
        console.error('Failed to fetch document count');
      }
    } catch (error) {
      console.error('Error updating document count:', error);
    }
  };

  useEffect(() => {
    updateDocumentCount();
  }, []);

  return (
    <div className="App">
      <h1>Document Search and QA System</h1>
      <DocumentUpload updateDocumentCount={updateDocumentCount} />
      <p>Total documents: {documentCount}</p>
      <DocumentList updateDocumentCount={updateDocumentCount} />
      <SearchInterface />
    </div>
  );
}

export default App;