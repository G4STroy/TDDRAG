import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.indexing_agent import IndexingAgent
from TDDRAG.config.config import config

@pytest.fixture
def indexing_agent(config):
    return IndexingAgent(config)

@pytest.mark.asyncio
async def test_index_document(indexing_agent, mocker):
    document = {
        "id": "test_id",
        "title": "Test Title",
        "content": "Test Content",
        "content_vector": [0.1] * 1536
    }
    
    mock_client = AsyncMock()
    mock_client.upload_documents = AsyncMock()
    mocker.patch.object(indexing_agent, 'get_search_client', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_client)))
    
    await indexing_agent.index_document(document)
    
    mock_client.upload_documents.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_documents(indexing_agent, mocker):
    document_ids = ["id1", "id2"]
    
    mock_client = AsyncMock()
    mock_client.upload_documents = AsyncMock()
    mocker.patch.object(indexing_agent, 'get_search_client', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_client)))
    
    await indexing_agent.delete_documents(document_ids)
    
    mock_client.upload_documents.assert_awaited_once()

@pytest.mark.asyncio
async def test_list_documents(indexing_agent, mocker):
    mock_docs = [
        {"id": "1", "content": "test1", "title": "Title 1", "author": "Author 1", "published_date": "2023-01-01", "key_phrases": "key1,key2"},
        {"id": "2", "content": "test2", "title": "Title 2", "author": "Author 2", "published_date": "2023-01-02", "key_phrases": "key3,key4"}
    ]

    async def async_iter(docs):
        for doc in docs:
            yield doc

    mock_client = AsyncMock()
    mock_client.search.return_value = async_iter(mock_docs)
    mocker.patch.object(indexing_agent, 'get_search_client', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_client)))

    result = await indexing_agent.list_documents()

    assert result == mock_docs