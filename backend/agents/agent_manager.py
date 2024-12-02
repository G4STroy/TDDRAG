# agent_manager.py
import logging
import aiohttp
import ssl
import certifi
import asyncio
from fastapi import logger as fastapi_logger
from .search_agent import SearchAgent
from .indexing_agent import IndexingAgent
from agents.document_processing import DocumentIngestionAgent
from agents.embedding_agent import EmbeddingAgent
from agents.llama3_llm import Llama3LLM
from agents.langchain_integration import LangchainAgent
from agents.document_enhancer import DocumentEnhancer
from config.config import Config  # Changed this line

class AgentManager:
    def __init__(self):
        self.config = Config()
        self.search_agent = None
        self.indexing_agent = None
        self.ingestion_agent = None
        self.embedding_agent = None
        self.llm = None
        self.langchain_agent = None

    async def initialize(self):
        try:
            logging.info("Initializing AgentManager")
            self.search_agent = SearchAgent()
            self.indexing_agent = IndexingAgent()
            self.ingestion_agent = DocumentIngestionAgent()
            self.embedding_agent = EmbeddingAgent()
            self.llm = Llama3LLM()

            initialization_tasks = [
                self.search_agent.initialize(),
                self.indexing_agent.initialize(),
                self.ingestion_agent.initialize(),
                self.embedding_agent.initialize(),
                self.llm.initialize(),
            ]

            await asyncio.gather(*initialization_tasks)

            self.langchain_agent = LangchainAgent(self.search_agent, self.embedding_agent, self.llm)
            await self.langchain_agent.initialize()

            logging.info("AgentManager initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing AgentManager: {str(e)}")
            raise

    async def cleanup(self):
        cleanup_tasks = [
            self.search_agent.cleanup() if self.search_agent else None,
            self.indexing_agent.cleanup() if self.indexing_agent else None,
            self.ingestion_agent.cleanup() if self.ingestion_agent else None,
            self.embedding_agent.cleanup() if self.embedding_agent else None,
            self.llm.cleanup() if self.llm else None,
            self.langchain_agent.cleanup() if self.langchain_agent else None
        ]
        await asyncio.gather(*[task for task in cleanup_tasks if task is not None])

agent_manager = AgentManager()


