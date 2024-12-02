# search_agent.py

import tracemalloc
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from config.config import Config
import logging
from typing import List, Dict, Any
import json
import asyncio
import aiohttp
import sys
import ssl

logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self, session: aiohttp.ClientSession = None, ssl_context: ssl.SSLContext = None):
        self.config = Config()
        self.client = None
        self.session = session or aiohttp.ClientSession()
        self.ssl_context = ssl_context or ssl.create_default_context()

    async def initialize(self):
        try:
            self.client = SearchClient(
                endpoint=self.config.AZURE_SEARCH_SERVICE_ENDPOINT,
                index_name=self.config.AZURE_SEARCH_INDEX_NAME,
                credential=AzureKeyCredential(self.config.AZURE_SEARCH_API_KEY),
                aiosession=self.session,
                connection_verify=self.ssl_context
            )
            logger.info("SearchAgent successfully initialized")
        except Exception as e:
            logger.error(f"Error initializing SearchAgent: {str(e)}")
            raise

    async def cleanup(self):
        try:
            if self.session:
                await self.session.close()
            logger.info("SearchAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during SearchAgent cleanup: {str(e)}")

    async def vector_search(self, query: str, top: int = 5):
        embedding = await self.generate_embedding(query)
        vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=top, fields="contentVector")
        results = await self.client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["id", "filename", "content", "key_phrases", "chunk_number", "title", "published_date", "author", "summary", "parent_id"],
            top=top
        )
        return [await self._process_result(result) async for result in results]

    async def hybrid_search(self, query: str, embedding: List[float], top: int = 5, filter: str = None, order_by: str = None) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Starting hybrid search with query: '{query}', embedding length: {len(embedding)}, top: {top}, filter: {filter}, order_by: {order_by}")
            vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=top, fields="contentVector")
            results = await self.client.search(
                search_text=query,
                vector_queries=[vector_query],
                filter=filter,
                order_by=order_by,
                select=["id", "parent_id", "title", "content", "published_date", "author", "key_phrases", "summary", "chunk_number", "filename"],
                top=top
            )
            processed_results = [await self._process_result(result) async for result in results]
            logger.info(f"Hybrid search completed. Found {len(processed_results)} results.")
            return processed_results
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}", exc_info=True)
            raise

    async def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        processed_result = {
            "id": result["id"],
            "filename": result["filename"],
            "title": result.get("title", ""),
            "content": result["content"],
            "published_date": result.get("published_date", ""),
            "author": result.get("author", ""),
            "key_phrases": result.get("key_phrases", []),
            "summary": result.get("summary", ""),
            "chunk_number": result.get("chunk_number", 0),
            "score": result["@search.score"],
            "captions": result.get("@search.captions", []),
        }
        return processed_result

    async def get_document_count(self) -> int:
        try:
            logger.debug(f"Search client: {self.client}")
            logger.debug(f"Attempting to search with parameters: '*', include_total_count=True, top=1")
            results = await self.client.search("*", include_total_count=True, top=1)
            count = await results.get_count()
            logger.info(f"Total documents in index: {count}")
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {str(e)}", exc_info=True)
            return None

    async def delete_documents(self, document_ids: list):
        try:
            results = await self.client.search("", 
                                         filter=" or ".join([f"id eq '{id}' or parent_id eq '{id}'" for id in document_ids]),
                                         select="id")
            all_ids = [result['id'] async for result in results]

            if not all_ids:
                logger.warning(f"No documents or chunks found for the given IDs")
                return False

            result = await self.client.delete_documents(documents=[{"id": doc_id} for doc_id in all_ids])

            if all(action.succeeded for action in result):
                logger.info(f"Selected documents and all related chunks deleted successfully from the index")
                return True
            else:
                failed_deletions = sum(1 for action in result if not action.succeeded)
                logger.error(f"Failed to delete {failed_deletions} items from the index")
                return False

        except Exception as e:
            logger.error(f"Error deleting selected documents from the index: {str(e)}")
            return False

    async def cleanup(self):
        try:
            if self.session:
                await self.session.close()
            logger.info("SearchAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during SearchAgent cleanup: {str(e)}")

async def main(action, *args):
    agent = SearchAgent()
    await agent.initialize()
    
    result = None
    try:
        if action == "vector_search":
            embedding = json.loads(args[0])
            top = int(args[1]) if len(args) > 1 else 5
            result = await agent.vector_search(embedding, top)
        elif action == "hybrid_search":
            query = args[0]
            embedding = json.loads(args[1])
            top = int(args[2]) if len(args) > 2 else 5
            result = await agent.hybrid_search(query, embedding, top)
        elif action == "get_document_count":
            result = await agent.get_document_count()
        elif action == "delete_documents":
            document_ids = json.loads(args[0])
            result = await agent.delete_documents(document_ids)
        else:
            raise ValueError(f"Unknown action: {action}")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)
        result = {"error": str(e)}
    finally:
        await agent.cleanup()
    
    return json.dumps({"result": result})

if __name__ == "__main__":
    tracemalloc.start()
    action = sys.argv[1]
    args = sys.argv[2:]
    result = asyncio.run(main(action, *args))
    print(result)
    tracemalloc.stop()