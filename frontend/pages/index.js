import { useState, useCallback, useEffect } from 'react';
import Head from 'next/head';
import axios from 'axios';
import DocumentUpload from '../components/DocumentUpload';
import SearchInterface from '../components/SearchInterface';
import DocumentDeletion from '../components/DocumentDeletion';
import DocumentList from '../components/DocumentList'; // Add this line

export default function Home() {
  const [activeTab, setActiveTab] = useState('upload');
  const [documentCount, setDocumentCount] = useState(null);
  const [countError, setCountError] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [indexedDocuments, setIndexedDocuments] = useState([]); // Add this line

  useEffect(() => {
    updateDocumentCount();
  }, []);

  const updateDocumentCount = useCallback(async () => {
    try {
      console.log('Fetching document count...');
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.get(`${backendUrl}/document_count`);
      console.log('Document count response:', response.data);
      setDocumentCount(response.data.count);
      setCountError(null);
    } catch (error) {
      console.error('Error fetching document count:', error.response?.data || error.message);
      setDocumentCount(null);
      setCountError(error.response?.data?.error || error.message);
    }
  }, []);

  const handleUpload = useCallback(async (file) => {
    if (!file) {
      setUploadStatus('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/uploadDocument', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Upload response:', response.data);
      setUploadStatus('File uploaded and indexed successfully!');
      updateDocumentCount();
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus(`Error uploading file: ${error.response?.data?.error || error.message}`);
    }
  }, [updateDocumentCount]);

  const fetchDocumentCount = async () => {
    try {
      console.log('Fetching document count...');
      const response = await fetch('/api/documentCount');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Document count response:', data);
      setDocumentCount(data.count);
    } catch (error) {
      console.error('Error fetching document count:', error);
      setDocumentCount(null);
      setCountError(error.message);
    }
  };

  const fetchIndexedDocuments = useCallback(async () => {
    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.get(`${backendUrl}/list_indexed_documents`);
      setIndexedDocuments(response.data.documents);
    } catch (error) {
      console.error('Error fetching indexed documents:', error.response?.data || error.message);
    }
  }, []);

  useEffect(() => {
    updateDocumentCount();
    fetchIndexedDocuments(); // Add this line
  }, [updateDocumentCount, fetchIndexedDocuments]); // Add fetchIndexedDocuments to the dependency array

  return (
    <div>
      <Head>
        <title>Document Processing and Search</title>
        <meta name="description" content="Document Processing and Search Application" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>Document Processing and Search Application</h1>

        <div>
          <button onClick={() => setActiveTab('upload')}>Upload & Index</button>
          <button onClick={() => setActiveTab('search')}>Search & Generate</button>
          <button onClick={() => setActiveTab('delete')}>Delete Documents</button>
          <button onClick={() => setActiveTab('list')}>List Documents</button>
        </div>

        {activeTab === 'upload' && (
          <DocumentUpload 
            onUpload={handleUpload} 
            uploadStatus={uploadStatus}
            updateDocumentCount={updateDocumentCount} 
          />
        )}
        {activeTab === 'search' && <SearchInterface />}
        {activeTab === 'delete' && (
          <DocumentDeletion updateDocumentCount={updateDocumentCount} />
        )}
        {activeTab === 'list' && (
          <DocumentList 
            documents={indexedDocuments} 
            updateDocumentCount={updateDocumentCount}
            fetchIndexedDocuments={fetchIndexedDocuments}
          />
        )}

        <div>
          {console.log('Rendering document count:', documentCount)}
          {documentCount !== null ? (
            `Total documents indexed: ${documentCount}`
          ) : countError ? (
            `Error: ${countError}`
          ) : (
            'Loading document count...'
          )}
        </div>
      </main>
    </div>
  );
}