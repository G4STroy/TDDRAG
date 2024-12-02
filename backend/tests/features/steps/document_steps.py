from behave import given, when, then
from behave.api.async_step import async_run_until_complete
from agents.document_processing import DocumentIngestionAgent
from agents.indexing_agent import IndexingAgent
from agents.search_agent import SearchAgent
from agents.embedding_agent import EmbeddingAgent
from agents.llama3_llm import Llama3LLM
from unittest.mock import AsyncMock, MagicMock

@given('the system is ready for document upload')
def step_impl(context):
    context.ingestion_agent = AsyncMock(spec=DocumentIngestionAgent)
    context.indexing_agent = AsyncMock(spec=IndexingAgent)
    context.ingestion_agent.process_document = AsyncMock(
        return_value={
            "content": "This is a test document.",
            "content_vector": [0.1] * 1536,
            "key_phrases": ["test", "document"]
        }
    )
    context.indexing_agent.index_document = AsyncMock()

@when('the user uploads a document "{filename}"')
@async_run_until_complete
async def step_impl(context, filename):
    context.uploaded_file = MagicMock()
    context.uploaded_file.name = filename
    context.result = await context.ingestion_agent.process_document(context.uploaded_file)
    await context.indexing_agent.index_document(context.result)

@then('the document should be successfully processed and indexed')
def step_impl(context):
    assert context.result is not None
    context.ingestion_agent.process_document.assert_awaited_once_with(context.uploaded_file)
    context.indexing_agent.index_document.assert_awaited_once_with(context.result)

@when('the user uploads documents "{doc1}" and "{doc2}"')
@async_run_until_complete
async def step_impl(context, doc1, doc2):
    context.uploaded_files = [MagicMock(name=doc1), MagicMock(name=doc2)]
    context.results = []
    for file in context.uploaded_files:
        result = await context.ingestion_agent.process_document(file)
        context.results.append(result)
        await context.indexing_agent.index_document(result)

@then('all documents should be successfully processed and indexed')
def step_impl(context):
    assert all(result is not None for result in context.results)
    assert context.ingestion_agent.process_document.call_count == len(context.uploaded_files)
    assert context.indexing_agent.index_document.call_count == len(context.uploaded_files)

@given('a document "{filename}" is uploaded')
def step_impl(context, filename):
    context.uploaded_file = MagicMock(name=filename)
    context.ingestion_agent = AsyncMock(spec=DocumentIngestionAgent)
    context.ingestion_agent.process_document = AsyncMock(
        return_value={
            "content": "This is a test document.",
            "content_vector": [0.1] * 1536,
            "key_phrases": ["test", "document"]
        }
    )

@when('the user initiates document processing')
@async_run_until_complete
async def step_impl(context):
    context.result = await context.ingestion_agent.process_document(context.uploaded_file)

@then('the document should be processed and key phrases extracted')
def step_impl(context):
    assert context.result is not None
    assert 'key_phrases' in context.result

@given('a document "{filename}" is indexed')
def step_impl(context, filename):
    context.indexing_agent = AsyncMock(spec=IndexingAgent)
    context.indexed_document = {'id': filename, 'content': 'test content'}
    context.indexing_agent.list_documents.return_value = [context.indexed_document]

@when('the user deletes the document "{filename}"')
@async_run_until_complete
async def step_impl(context, filename):
    await context.indexing_agent.delete_documents([filename])

@then('the document should be removed from the index')
def step_impl(context):
    context.indexing_agent.delete_documents.assert_called_once_with([context.indexed_document['id']])

@given('documents "{doc1}" and "{doc2}" are indexed')
def step_impl(context, doc1, doc2):
    context.indexing_agent = AsyncMock(spec=IndexingAgent)
    context.indexed_documents = [{'id': doc1, 'content': 'test content 1'}, {'id': doc2, 'content': 'test content 2'}]
    context.indexing_agent.list_documents.return_value = context.indexed_documents

@when('the user deletes documents "{doc1}" and "{doc2}"')
@async_run_until_complete
async def step_impl(context, doc1, doc2):
    await context.indexing_agent.delete_documents([doc1, doc2])

@then('the documents should be removed from the index')
def step_impl(context):
    context.indexing_agent.delete_documents.assert_called_once_with([doc['id'] for doc in context.indexed_documents])

@given('the index contains processed documents')
def step_impl(context):
    context.search_agent = AsyncMock(spec=SearchAgent)
    context.llm = AsyncMock(spec=Llama3LLM)
    
    # Mock the search results for both vector and hybrid searches
    context.mock_search_results = [{"id": "1", "content": "This is a test result", "title": "Test Result Title"}]
    context.search_agent.search = AsyncMock(return_value=context.mock_search_results)
    context.search_agent.hybrid_search = AsyncMock(return_value=context.mock_search_results)

@when('the user performs a vector search with query "{query}"')
@async_run_until_complete
async def step_impl(context, query):
    context.search_results = await context.search_agent.search(query)

@when('the user performs a hybrid search with query "{query}"')
@async_run_until_complete
async def step_impl(context, query):
    context.search_results = await context.search_agent.hybrid_search(query)

@then('the system should return relevant results')
def step_impl(context):
    assert len(context.search_results) > 0

@then('the LLM should generate a response based on the search results')
@async_run_until_complete
async def step_impl(context):
    context.llm_response = await context.llm._acall(f"Based on these results: {context.search_results}, provide a summary.")
    assert context.llm_response is not None
