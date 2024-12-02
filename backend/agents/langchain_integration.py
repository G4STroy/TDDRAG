# langchain_integration.py
import asyncio
import json
import sys
from langchain_community.retrievers import AzureAISearchRetriever
from langchain.memory import ConversationBufferMemory
from config.config import Config
from .search_agent import SearchAgent
from .embedding_agent import EmbeddingAgent
from .llama3_llm import Llama3LLM
from typing import List, Dict
import logging
import aiohttp

logger = logging.getLogger(__name__)

class LangchainAgent:
    def __init__(self, search_agent: SearchAgent, embedding_agent: EmbeddingAgent, llm: Llama3LLM):
        self.search_agent = search_agent
        self.embedding_agent = embedding_agent
        self.llm = llm
        self.retriever = None
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.session = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()
        self.retriever = await self._create_retriever()

    async def _create_retriever(self):
        config = Config()
        return AzureAISearchRetriever(
            service_name=config.AZURE_SEARCH_SERVICE_NAME,
            index_name=config.AZURE_SEARCH_INDEX_NAME,
            api_key=config.AZURE_SEARCH_API_KEY,
            content_key="content",
            top_k=5,
            aiosession=self.session
        )

    async def cleanup(self):
        if self.retriever:
            if hasattr(self.retriever, 'aiosession') and self.retriever.aiosession:
                await self.retriever.aiosession.close()
        if self.session:
            await self.session.close()
        # Clear the memory
        self.memory.clear()
        logger.info("LangchainAgent cleanup completed.")

    async def process_query(self, query: str, search_type: str):
        try:
            embedding = await self.embedding_agent.generate_embedding(query)
            if search_type == "Vector":
                search_results = await self.search_agent.vector_search(embedding)
            elif search_type == "Hybrid":
                search_results = await self.search_agent.hybrid_search(query, embedding)
            else:
                raise ValueError(f"Invalid search type: {search_type}")

            context = "\n".join([result['content'] for result in search_results])
            has_relevant_context = len(context.strip()) > 0
            if not has_relevant_context:
                context = "There is no specific context provided from the uploaded documents for the following question."

            chat_history = self.memory.chat_memory.messages
            prompt = self._create_prompt(context, query, chat_history)
            llm_response = await self.llm.generate_response(prompt)

            # Update memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(llm_response)

            logger.info(f"Context being passed to LLM: {context[:500]}...")
            logger.info(f"LLM response: {llm_response}")

            return search_results, llm_response
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def _create_prompt(self, context: str, query: str, chat_history: List[Dict[str, str]]) -> str:
        history_str = "\n".join([f"Human: {msg['content']}" if msg['type'] == 'human' else f"AI: {msg['content']}" for msg in chat_history])
        return f"""Previous conversation:
{history_str}

Context:
{context}
"""

async def main(query, search_type):
    search_agent = SearchAgent()
    embedding_agent = EmbeddingAgent()
    llm = Llama3LLM()
    
    await search_agent.initialize()
    await embedding_agent.initialize()
    await llm.initialize()
    
    agent = LangchainAgent(search_agent, embedding_agent, llm)
    await agent.initialize()
    
    search_results, llm_response = await agent.process_query(query, search_type)
    
    await agent.cleanup()
    await search_agent.cleanup()
    await embedding_agent.cleanup()
    await llm.cleanup()
    
    return json.dumps({"search_results": search_results, "llm_response": llm_response})

if __name__ == "__main__":
    query = sys.argv[1]
    search_type = sys.argv[2]
    result = asyncio.run(main(query, search_type))
    print(result)