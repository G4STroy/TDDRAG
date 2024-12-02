import sys
import os
# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
from unittest.mock import Mock, patch
from TDDRAG.config.config import Config
from unittest.mock import MagicMock

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "scenario_1: mark test as scenario 1"
    )
    config.addinivalue_line(
        "markers", "scenario_2: mark test as scenario 2"
    )

@pytest.fixture(scope="session")
def config():
    # Ensure environment variables are loaded
    os.environ["COHERE_API_KEY"] = "test_api_key"
    os.environ["LANGUAGE_SERVICE_ENDPOINT"] = "https://mock-language.cognitiveservices.azure.com/"
    os.environ["LANGUAGE_SERVICE_KEY"] = "mock_language_key"
    os.environ["AZURE_SEARCH_ENDPOINT"] = "https://mock-search.search.windows.net"
    os.environ["AZURE_SEARCH_KEY"] = "mock_search_key"
    os.environ["AZURE_SEARCH_INDEX_NAME"] = "tddrag-index"
    os.environ["AZURE_BLOB_ACCOUNT_NAME"] = "mockaccount"
    os.environ["AZURE_BLOB_ACCOUNT_KEY"] = "mock_account_key"
    os.environ["AZURE_BLOB_CONTAINER_NAME"] = "mock-container"
    os.environ["AZURE_LLAMA3_ENDPOINT"] = "https://mock-llama3.openai.azure.com/"
    os.environ["AZURE_LLAMA3_KEY"] = "mock_llama3_key"
    return Config()

@pytest.fixture(autouse=True)
def mock_cohere_client(monkeypatch):
    class MockCohereClient:
        def embed(self, texts, model=None, input_type=None, truncate=None, **kwargs):
            return [[0.1] * 4096 for _ in texts]
    
    mock_client = Mock(spec=MockCohereClient)
    mock_client.embed.side_effect = MockCohereClient().embed
    monkeypatch.setattr("cohere.Client", lambda *args, **kwargs: mock_client)

@pytest.fixture
def mock_cohere_embeddings():
    with patch('langchain_cohere.CohereEmbeddings') as mock:
        mock_instance = mock.return_value
        mock_instance.embed_query.return_value = [0.1] * 4096
        mock_instance.embed_documents.return_value = [[0.1] * 4096 for _ in range(10)]
        mock_instance.client = MagicMock()

        # Create a new class that inherits from MagicMock and handles the timeout parameter
        class TimeoutMock(MagicMock):
            def __call__(self, *args, **kwargs):
                kwargs.pop('timeout', None)  # Remove the timeout parameter if it exists
                return super().__call__(*args, **kwargs)

        # Use the TimeoutMock for the CohereEmbeddings mock
        mock.side_effect = TimeoutMock

        yield mock

@pytest.fixture
def mock_azure_search():
    with patch('langchain_community.vectorstores.AzureSearch') as mock:
        mock_instance = mock.return_value
        mock_instance.as_retriever.return_value = Mock()
        yield mock_instance

@pytest.fixture
def mock_text_analytics_client():
    with patch('azure.ai.textanalytics.TextAnalyticsClient') as mock:
        yield mock.return_value

@pytest.fixture
def mock_text_splitter():
    with patch('langchain.text_splitter.RecursiveCharacterTextSplitter') as mock:
        yield mock.return_value

@pytest.fixture
def mock_blob_service_client():
    with patch('azure.storage.blob.BlobServiceClient') as mock:
        yield mock.return_value

@pytest.fixture
def mock_document_ingestion_agent():
    with patch('TDDRAG.agents.document_processing.DocumentIngestionAgent') as mock:
        yield mock.return_value

@pytest.fixture
def mock_indexing_agent():
    with patch('TDDRAG.agents.indexing.IndexingAgent') as mock:
        yield mock.return_value

@pytest.fixture
def mock_search_agent():
    with patch('TDDRAG.agents.search_agent.SearchAgent') as mock:
        yield mock.return_value

