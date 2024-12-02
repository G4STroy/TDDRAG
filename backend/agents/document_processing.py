# document_processing.py
import asyncio
import json
import sys
import os
from datetime import datetime
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import logging
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
import yaml
import openai
from openai import AsyncAzureOpenAI
from config.config import Config
from azure.ai.textanalytics import TextAnalyticsClient
from .document_enhancer import DocumentEnhancer
import re

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Change the relative import to an absolute import
from config.config import Config

logger = logging.getLogger(__name__)

class DocumentIngestionAgent:
    def __init__(self):
        self.config = Config()
        self.text_analytics_client = None
        if not self.config.AZURE_LANGUAGE_SERVICE_ENDPOINT or not self.config.AZURE_LANGUAGE_SERVICE_API_KEY:
            raise ValueError("AZURE_LANGUAGE_SERVICE_ENDPOINT or AZURE_LANGUAGE_SERVICE_API_KEY not set in the .env file.")
        
        try:
            self.text_analytics_client = TextAnalyticsClient(
                endpoint=self.config.AZURE_LANGUAGE_SERVICE_ENDPOINT,
                credential=AzureKeyCredential(self.config.AZURE_LANGUAGE_SERVICE_API_KEY)
            )
            logger.info("TextAnalyticsClient initialized successfully")
        except ValueError as e:
            logger.error(f"Error initializing TextAnalyticsClient: {str(e)}")
            raise

        self.connection_string = self.config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = self.config.AZURE_STORAGE_CONTAINER_NAME
        self.client = None
        self.search_client = None
        self.openai_client = AsyncAzureOpenAI(
            api_key=self.config.AZURE_OPENAI_API_KEY,
            api_version=self.config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=self.config.AZURE_OPENAI_ENDPOINT
        )
        self.document_enhancer = DocumentEnhancer()

    async def initialize(self):
        try:
            logger.info("Initializing DocumentIngestionAgent")
            self.client = BlobServiceClient.from_connection_string(self.connection_string)
            logger.debug(f"BlobServiceClient initialized with endpoint: {self.client.url}")
            self.search_client = SearchClient(
                endpoint=self.config.AZURE_SEARCH_SERVICE_ENDPOINT,
                index_name=self.config.AZURE_SEARCH_INDEX_NAME,
                credential=AzureKeyCredential(self.config.AZURE_SEARCH_API_KEY)
            )
            logger.debug(f"SearchClient initialized with endpoint: {self.config.AZURE_SEARCH_SERVICE_ENDPOINT}")
            logger.debug(f"SearchClient index name: {self.config.AZURE_SEARCH_INDEX_NAME}")
            await self.document_enhancer.initialize()
            logger.info("DocumentIngestionAgent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DocumentIngestionAgent: {str(e)}")
            raise

    def sanitize_filename(self, filename):
        # Replace spaces and other invalid characters with underscores
        return re.sub(r'[^\w\-=]', '_', filename)

    async def upload_document(self, filename, content):
        print(f"DEBUG: Starting upload_document for {filename}")
        if not self.client:
            print("DEBUG: Initializing client")
            await self.initialize()

        container_client = self.client.get_container_client(self.container_name)

        try:
            print("DEBUG: Creating container")
            await container_client.create_container()
        except ResourceExistsError:
            print("DEBUG: Container already exists")
            pass

        blob_client = container_client.get_blob_client(filename)

        try:
            print(f"DEBUG: Uploading blob for {filename}")
            await blob_client.upload_blob(content, overwrite=True)
            logger.info(f"Uploaded {filename} to Azure Blob storage")
            print(f"DEBUG: Blob upload successful for {filename}")

            # Parse the content
            content_str = content.decode('utf-8')
            content_parts = content_str.split('---\n', 2)
            metadata = {}
            if len(content_parts) > 2:
                metadata_yaml = content_parts[1]
                metadata = yaml.safe_load(metadata_yaml)
                main_content = content_parts[2]
            else:
                main_content = content_str

            sanitized_filename = self.sanitize_filename(filename)
            document = {
                "id": sanitized_filename,
                "filename": filename,
                "content": main_content,
                "language": "en",  # Or use language detection
                "title": metadata.get("title", ""),
                "published_date": metadata.get("published_date", None),
                "author": metadata.get("author", ""),
                "key_phrases": metadata.get("key_phrases", []),
                "summary": metadata.get("summary", ""),
            }

            # After successful blob upload, index the document
            try:
                result = await self.search_client.upload_documents(documents=[document])
                if result[0].succeeded:
                    logger.info(f"Document {filename} indexed successfully")
                    return True
                else:
                    logger.error(f"Failed to index document {filename}")
                    return False
            except Exception as e:
                logger.error(f"Error indexing document {filename}: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error uploading or indexing {filename}: {str(e)}")
            logger.exception("Full traceback:")
            print(f"DEBUG: Exception occurred: {str(e)}")
            return False

    async def search_existing_document(self, filename):
        results = await self.search_client.search(
            search_text="",
            filter=f"filename eq '{filename}'",
            select="id,filename",
            top=1
        )
        async for result in results:
            return result
        return None

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
                await self.client.get_blob_client(self.container_name, filename).delete_blob()

            logger.info("All documents and associated data deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting all documents: {str(e)}")
            return False

    async def delete_documents(self, file_names):
        if not self.client:
            await self.initialize()

        container_client = self.client.get_container_client(self.container_name)

        try:
            for file_name in file_names:
                await container_client.delete_blob(file_name)
            logger.info(f"Deleted selected documents from Blob storage")
            return True
        except Exception as e:
            logger.error(f"Error deleting selected documents from Blob storage: {str(e)}")
            return False

    async def list_documents(self):
        try:
            documents = await self.search_client.list_documents()
            return [doc['id'] for doc in documents]
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise

    async def cleanup(self):
        try:
            if self.client:
                await self.client.close()
            if self.search_client:
                await self.search_client.close()
            if self.openai_client:
                await self.openai_client.close()
            await self.document_enhancer.cleanup()
            logger.info("DocumentIngestionAgent cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during DocumentIngestionAgent cleanup: {str(e)}")

async def main(action, *args):
    agent = DocumentIngestionAgent()
    try:
        await agent.initialize()
        result = False
        message = ""
        print("DEBUG: Starting main function")
        print(f"DEBUG: Action: {action}, Args: {args}")
        if action == "upload":
            file_name, file_path = args
            print(f"DEBUG: Uploading file: {file_name}")
            with open(file_path, 'rb') as file:
                file_content = file.read()
            result = await agent.upload_document(file_name, file_content)
            message = "File uploaded successfully" if result else "Failed to upload file"
        elif action == "delete_all":
            print("DEBUG: Deleting all documents")
            result = await agent.delete_all_documents()
            message = "All documents deleted" if result else "Failed to delete all documents"
        elif action == "delete":
            print("DEBUG: Deleting selected documents")
            result = await agent.delete_documents(json.loads(args[0]))
            message = "Selected documents deleted" if result else "Failed to delete selected documents"
        elif action == "list":
            print("DEBUG: Listing documents")
            documents = await agent.list_documents()
            result = True
            message = json.dumps(documents)
        else:
            message = f"Unknown action: {action}"
            print(f"ERROR: {message}")
        return result, message
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        return False, str(e)
    finally:
        await agent.cleanup()