import { useState } from 'react';

export default function SearchInterface() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('Vector');
  const [results, setResults] = useState([]);
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/searchDocuments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, searchType }),
      });

      const data = await response.json();
      setResults(data.results);
      setConversation([...conversation, { role: 'user', content: query }, { role: 'ai', content: data.llmResponse }]);
    } catch (error) {
      console.error('Error searching documents:', error);
      alert('An error occurred while searching. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Search and Chat</h2>
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query"
        />
        <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
          <option value="Vector">Vector</option>
          <option value="Hybrid">Hybrid</option>
        </select>
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div>
        <h3>Conversation</h3>
        {conversation.map((entry, index) => (
          <div key={index}>
            <strong>{entry.role === 'user' ? 'You:' : 'AI:'}</strong> {entry.content}
          </div>
        ))}
      </div>

      <div>
        <h3>Search Results</h3>
        {results.map((result, index) => (
          <div key={index}>
            <h4>{result.title}</h4>
            <p>{result.content.substring(0, 200)}...</p>
            {result.summary && <p>Summary: {result.summary}</p>}
            {result.key_phrases && <p>Key Phrases: {result.key_phrases.join(', ')}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}