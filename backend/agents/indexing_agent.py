# indexing_agent.py
import asyncio
import json
import sys
import logging
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
import logging
from config.config import Config
import aiohttp
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

class IndexingAgent:
    def __init__(self):
        self.config = Config()
        self.search_client = None
        self.blob_service_client = None

    async def initialize(self):
        try:
            logger.info("Initializing IndexingAgent")
            logger.debug(f"AZURE_SEARCH_SERVICE_ENDPOINT: {self.config.AZURE_SEARCH_SERVICE_ENDPOINT}")
            logger.debug(f"AZURE_SEARCH_INDEX_NAME: {self.config.AZURE_SEARCH_INDEX_NAME}")
            logger.debug(f"AZURE_SEARCH_API_KEY: {'*' * len(self.config.AZURE_SEARCH_API_KEY)}")
            self.search_client = SearchClient(
                endpoint=self.config.AZURE_SEARCH_SERVICE_ENDPOINT,
                index_name=self.config.AZURE_SEARCH_INDEX_NAME,
                credential=AzureKeyCredential(self.config.AZURE_SEARCH_API_KEY)
            )
            self.blob_service_client = BlobServiceClient.from_connection_string(self.config.AZURE_STORAGE_CONNECTION_STRING)
            logger.info("IndexingAgent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing IndexingAgent: {str(e)}")
            logger.exception("Full traceback:")
            raise

    async def delete_all_documents(self):
        try:
            logger.info("Starting deletion of all documents")
            results = await self.search_client.search("*", select="id,filename", top=1000)
            all_docs = {}
            async for result in results:
                if result['filename'] not in all_docs:
                    all_docs[result['filename']] = []
                all_docs[result['filename']].append(result['id'])

            for filename, chunk_ids in all_docs.items():
                logger.debug(f"Deleting chunks for file: {filename}")
                await self.search_client.delete_documents(documents=[{"id": chunk_id} for chunk_id in chunk_ids])
                logger.debug(f"Deleting blob for file: {filename}")
                await self.blob_service_client.get_blob_client(self.config.AZURE_STORAGE_CONTAINER_NAME, filename).delete_blob()

            logger.info("All documents and associated data deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting all documents: {str(e)}")
            return False

    async def delete_documents(self, file_names: list):
        try:
            for file_name in file_names:
                # Delete all chunks associated with the file
                results = await self.search_client.search("",
                                                          filter=f"parent_id eq '{file_name}'",
                                                          select="id")
                chunk_ids = [result['id'] async for result in results]
                
                if chunk_ids:
                    result = await self.search_client.delete_documents(documents=[{"id": chunk_id} for chunk_id in chunk_ids])
                    if not all(action.succeeded for action in result):
                        logger.error(f"Failed to delete some chunks for {file_name}")
                        return False

                # Delete the parent document
                result = await self.search_client.delete_documents(documents=[{"id": file_name}])
                if not all(action.succeeded for action in result):
                    logger.error(f"Failed to delete parent document {file_name}")
                    return False

            logger.info(f"Selected documents and their chunks deleted successfully")
            await self.update_document_count()
            return True
        except Exception as e:
            logger.error(f"Error deleting selected documents: {str(e)}")
            return False

    async def update_document_count(self):
        try:
            count = await self.get_document_count()
            # You might need to implement a way to store this count,
            # either in a database or a file, depending on your setup
            self.logger.info(f"Updated document count: {count}")
        except Exception as e:
            self.logger.error(f"Error updating document count: {str(e)}")

    async def get_document_count(self):
        try:
            results = await self.search_client.search("*", include_total_count=True, top=0)
            count = await results.get_count()
            logger.info(f"Total indexed items: {count}")
            return count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            raise

    async def cleanup(self):
        try:
            if self.search_client:
                await self.search_client.close()
            if self.blob_service_client:
                await self.blob_service_client.close()
            logger.info("IndexingAgent cleanup completed.")
        except Exception as e:
            logger.error(f"Error during IndexingAgent cleanup: {str(e)}")

    async def list_documents(self):
        try:
            results = await self.search_client.search("*", 
                                                      select="id,filename,title,author,published_date",
                                                      top=1000)
            documents = [
                {
                    "id": doc["id"],
                    "filename": doc.get("filename", ""),
                    "title": doc.get("title", ""),
                    "author": doc.get("author", ""),
                    "published_date": doc.get("published_date", "")
                }
                async for doc in results
            ]
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    async def list_indexed_documents(self):
        try:
            results = await self.search_client.search("*", 
                                                      select="id,filename,title",
                                                      top=1000)
            documents = [
                {
                    "id": doc["id"],
                    "filename": doc.get("filename", ""),
                    "title": doc.get("title", "")
                }
                async for doc in results
            ]
            return documents
        except Exception as e:
            logger.error(f"Error listing indexed documents: {str(e)}")
            raise

async def main(action, *args):
    agent = IndexingAgent()
    await agent.initialize()
    
    result = None
    if action == "delete_all":
        result = await agent.delete_all_documents()
    elif action == "delete":
        result = await agent.delete_documents(json.loads(args[0]))
    elif action == "count":
        result = await agent.get_document_count()
    elif action == "list":
        result = await agent.list_documents()

    await agent.cleanup()
    
    return json.dumps({"result": result})

if __name__ == "__main__":
    action = sys.argv[1]
    args = sys.argv[2:]
    result = asyncio.run(main(action, *args))
    print(result)