import pytest
from unittest.mock import AsyncMock, MagicMock
from io import BytesIO
from agents.document_processing import DocumentIngestionAgent
from TDDRAG.config.config import config

@pytest.fixture
def document_ingestion_agent(config):
    return DocumentIngestionAgent(config)

@pytest.mark.asyncio
async def test_process_document_txt(document_ingestion_agent, mocker):
    content = "This is a test document."
    file = BytesIO(content.encode('utf-8'))
    file.name = "test.txt"

    mocker.patch('langchain_community.document_loaders.TextLoader.load', return_value=[MagicMock(page_content=content)])
    mocker.patch.object(document_ingestion_agent.text_splitter, 'split_text', return_value=[content])
    mocker.patch.object(document_ingestion_agent.text_analytics_client, 'extract_key_phrases', return_value=[MagicMock(key_phrases=["test", "document"])])
    mocker.patch.object(document_ingestion_agent.embedding_agent, 'generate_embedding', return_value=[0.1] * 1536)

    result = await document_ingestion_agent.process_document(file)

    assert result["content"] == content
    assert len(result["content_vector"]) == 1536

@pytest.mark.asyncio
async def test_process_document_pdf(document_ingestion_agent, mocker):
    content = "This is a test PDF document."
    file = BytesIO(b"fake pdf content")
    file.name = "test.pdf"

    mocker.patch('langchain_community.document_loaders.PyPDFLoader.load', return_value=[MagicMock(page_content=content)])
    mocker.patch.object(document_ingestion_agent.text_splitter, 'split_text', return_value=[content])
    mocker.patch.object(document_ingestion_agent.text_analytics_client, 'extract_key_phrases', return_value=[MagicMock(key_phrases=["test", "PDF", "document"])])
    mocker.patch.object(document_ingestion_agent.embedding_agent, 'generate_embedding', return_value=[0.1] * 1536)

    result = await document_ingestion_agent.process_document(file)

    assert result["content"] == content
    assert len(result["content_vector"]) == 1536

@pytest.mark.asyncio
async def test_unsupported_file_type(document_ingestion_agent):
    file = BytesIO(b"fake content")
    file.name = "test.docx"

    with pytest.raises(ValueError, match="Unsupported file type"):
        await document_ingestion_agent.process_document(file)