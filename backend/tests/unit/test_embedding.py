import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.embedding_agent import EmbeddingAgent
from TDDRAG.config.config import config

@pytest.fixture
def embedding_agent(config):
    return EmbeddingAgent(config)

@pytest.mark.asyncio
async def test_generate_embedding(embedding_agent, mocker):
    text = "This is a test text"
    
    result = await embedding_agent.generate_embedding(text)

    assert len(result) == 1536
    assert all(isinstance(x, float) for x in result)

@pytest.mark.asyncio
async def test_get_embedding_dimension(embedding_agent, mocker):
    expected_dimension = 1536

    mock_embeddings = AsyncMock()
    mock_embeddings.embed_query.return_value = [0.1] * expected_dimension
    mocker.patch('langchain_openai.AzureOpenAIEmbeddings', return_value=mock_embeddings)

    result = await embedding_agent.get_embedding_dimension()

    assert result == expected_dimension