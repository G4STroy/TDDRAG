import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.search_agent import SearchAgent
from config.config import config
from agents.embedding_agent import EmbeddingAgent
import aiohttp
from metadata_parser import MetadataParser

@pytest.fixture
def mock_embedding_agent():
    agent = AsyncMock(spec=EmbeddingAgent)
    agent.generate_embedding.return_value = [0.1] * 1536
    return agent

@pytest.fixture
def search_agent(config, mock_embedding_agent):
    agent = SearchAgent(config, mock_embedding_agent)
    agent.metadata_parser = MetadataParser(search_head_only=True)
    return agent

class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

@pytest.mark.asyncio
async def test_search(search_agent, mocker):
    query = "test query"
    mock_results = [
        {"id": "1", "content": "test content", "title": "Test Title", "author": "Test Author", "published_date": "2023-01-01", "key_phrases": "key1,key2", "relevance_score": None}
    ]

    mock_client = AsyncMock()
    mock_client.search.return_value = AsyncIterator(mock_results)
    mocker.patch.object(search_agent, 'create_search_client', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_client)))
    mocker.patch.object(search_agent, 'ensure_index_exists', AsyncMock())

    result = await search_agent.search(query)

    assert result == mock_results
    search_agent.create_search_client.assert_called_once()
    search_agent.ensure_index_exists.assert_called_once()

@pytest.mark.asyncio
async def test_hybrid_search(search_agent, mocker):
    query = "test query"
    mock_results = [
        {"id": "1", "content": "test content", "title": "Test Title", "author": "Test Author", "published_date": "2023-01-01", "key_phrases": "key1,key2", "relevance_score": None}
    ]

    mock_client = AsyncMock()
    mock_client.search.return_value = AsyncIterator(mock_results)
    mocker.patch.object(search_agent, 'create_search_client', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_client)))
    mocker.patch.object(search_agent, 'ensure_index_exists', AsyncMock())

    result = await search_agent.hybrid_search(query)

    assert result == mock_results
    search_agent.create_search_client.assert_called_once()
    search_agent.ensure_index_exists.assert_called_once()

@pytest.mark.asyncio
async def test_generate_llm_response(search_agent, mocker):
    prompt = "test prompt"
    mock_response = "This is a test response"
    
    # Mock response object
    mock_response_obj = AsyncMock()
    mock_response_obj.__aenter__.return_value = mock_response_obj
    mock_response_obj.__aexit__.return_value = None
    mock_response_obj.json.return_value = {"choices": [{"message": {"content": mock_response}}]}
    mock_response_obj.raise_for_status = AsyncMock()  # Add this line
    
    # Mock the session.post method to return the mock response object
    mock_session = mocker.patch('aiohttp.ClientSession.post', return_value=mock_response_obj)
    
    # Set necessary attributes
    mocker.patch.object(search_agent, 'llm_endpoint_url', "http://mock-url")
    mocker.patch.object(search_agent, 'llm_api_key', "mock-api-key")
    
    result = await search_agent.generate_llm_response(prompt)
    
    assert result == mock_response
    mock_session.assert_called_once_with(
        "http://mock-url",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer mock-api-key"
        },
        json={
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
    )
