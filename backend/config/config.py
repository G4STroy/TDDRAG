import os
from pathlib import Path
from dotenv import load_dotenv
from typing import ClassVar
import logging

# Get the path to the backend directory
backend_dir = Path(__file__).resolve().parent.parent

# Load the .env file from the backend directory
load_dotenv(backend_dir / '.env')

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Config:
    # Azure AI Search
    AZURE_SEARCH_SERVICE_NAME = os.getenv('AZURE_SEARCH_SERVICE_NAME')
    AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME')
    AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
    AZURE_SEARCH_SERVICE_ENDPOINT = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net"
    AZURE_SEARCH_ENDPOINT = f"https://{AZURE_SEARCH_SERVICE_NAME}.search.windows.net"

    # Azure OpenAI
    AZURE_OPENAI_API_KEY: ClassVar[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: ClassVar[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: ClassVar[str] = os.getenv("AZURE_OPENAI_API_VERSION")

    # Azure OpenAI Deployments
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: ClassVar[str] = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    AZURE_OPENAI_EMBEDDING_MODEL: ClassVar[str] = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
    AZURE_OPENAI_EMBEDDING_DIMENSIONS: ClassVar[int] = 1536

    # Azure Blob Storage
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER_NAME = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    AZURE_STORAGE_API_KEY = os.getenv('AZURE_STORAGE_API_KEY')

    # Azure Language Service for Text Analytics 
    AZURE_LANGUAGE_SERVICE_NAME: ClassVar[str] = os.getenv("AZURE_LANGUAGE_SERVICE_NAME")
    AZURE_LANGUAGE_SERVICE_ENDPOINT: ClassVar[str] = os.getenv("AZURE_LANGUAGE_SERVICE_ENDPOINT")
    
    @property
    def AZURE_LANGUAGE_SERVICE_API_KEY(self) -> str:
        return os.getenv("AZURE_LANGUAGE_SERVICE_API_KEY", "")

    @property
    def AZURE_LANGUAGE_SERVICE_ENDPOINT(self) -> str:
        return os.getenv("AZURE_LANGUAGE_SERVICE_ENDPOINT", "")

    # Azure AI Studio Project
    AZURE_AI_STUDIO_PROJECT_NAME: ClassVar[str] = os.getenv("AZURE_AI_STUDIO_PROJECT_NAME")

    # Other configurations
    INDEXER_NAME: ClassVar[str] = os.getenv("INDEXER_NAME")
    SKILLSET_NAME: ClassVar[str] = os.getenv("SKILLSET_NAME")
    DATA_SOURCE_NAME: ClassVar[str] = os.getenv("DATA_SOURCE_NAME")

    # Meta-Llama-3.1-70B-Instruct
    META_LLAMA_ENDPOINT: ClassVar[str] = os.getenv("META_LLAMA_ENDPOINT")
    META_LLAMA_API_KEY: ClassVar[str] = os.getenv("META_LLAMA_API_KEY")
    META_LLAMA_CHAT_ENDPOINT: ClassVar[str] = f"{META_LLAMA_ENDPOINT}/v1/chat/completions"

    def __init__(self):
        logger.debug("Initializing Config object")
        logger.debug(f"AZURE_SEARCH_SERVICE_NAME: {self.AZURE_SEARCH_SERVICE_NAME}")
        logger.debug(f"AZURE_SEARCH_INDEX_NAME: {self.AZURE_SEARCH_INDEX_NAME}")
        logger.debug(f"AZURE_SEARCH_API_KEY: {'*' * len(self.AZURE_SEARCH_API_KEY) if self.AZURE_SEARCH_API_KEY else 'Not set'}")
        logger.debug(f"AZURE_SEARCH_SERVICE_ENDPOINT: {self.AZURE_SEARCH_SERVICE_ENDPOINT}")
        logger.debug(f"AZURE_SEARCH_ENDPOINT: {self.AZURE_SEARCH_ENDPOINT}")
        logger.debug(f"AZURE_LANGUAGE_SERVICE_NAME: {self.AZURE_LANGUAGE_SERVICE_NAME}")
        logger.debug(f"AZURE_LANGUAGE_SERVICE_ENDPOINT: {self.AZURE_LANGUAGE_SERVICE_ENDPOINT}")
        logger.debug(f"AZURE_LANGUAGE_SERVICE_API_KEY: {'*' * len(self.AZURE_LANGUAGE_SERVICE_API_KEY) if self.AZURE_LANGUAGE_SERVICE_API_KEY else 'Not set'}")
        # Add similar debug logs for other configuration variables

    @classmethod
    def is_valid(cls) -> bool:
        required_vars = [
            "AZURE_SEARCH_SERVICE_NAME", "AZURE_SEARCH_INDEX_NAME", "AZURE_SEARCH_API_KEY",
            "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "AZURE_OPENAI_EMBEDDING_MODEL",
            "AZURE_STORAGE_CONNECTION_STRING", "AZURE_STORAGE_CONTAINER_NAME", "AZURE_STORAGE_API_KEY",
            "META_LLAMA_ENDPOINT", "META_LLAMA_API_KEY"
        ]
        return all(getattr(cls, var) for var in required_vars)

config = Config()

print(f"AZURE_SEARCH_SERVICE_NAME: {os.getenv('AZURE_SEARCH_SERVICE_NAME')}")
print(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
print(f"AZURE_SEARCH_API_KEY: {os.getenv('AZURE_SEARCH_API_KEY')}")