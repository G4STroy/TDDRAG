# embedding_agent.py
import asyncio
import json
import sys
from typing import List, Tuple
import numpy as np
from openai import AsyncAzureOpenAI
from config.config import config
import logging
import httpx
from .cache import async_cache
from scipy import spatial

logger = logging.getLogger(__name__)

import os
print("Python path:", sys.path)
print("Current directory:", os.getcwd())

class EmbeddingAgent:
    def __init__(self):
        self.client = None
        self.http_client = None
        self.deployment = config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.model = "text-embedding-ada-002"  # or whatever model you're using

    async def initialize(self):
        self.http_client = httpx.AsyncClient()
        self.client = AsyncAzureOpenAI(
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            http_client=self.http_client
        )

    @async_cache
    async def generate_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        try:
            response = await self.client.embeddings.create(
                input=[text],
                model=self.deployment
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        assert len(texts) <= 2048, "The batch size should not be larger than 2048."
        texts = [text.replace("\n", " ") for text in texts]
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self.deployment
            )
            return [d.embedding for d in response.data]
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def distances_from_embeddings(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        distance_metric: str = "cosine"
    ) -> List[float]:
        distance_metrics = {
            "cosine": spatial.distance.cosine,
            "L1": spatial.distance.cityblock,
            "L2": spatial.distance.euclidean,
            "Linf": spatial.distance.chebyshev,
        }
        distances = [
            distance_metrics[distance_metric](query_embedding, embedding)
            for embedding in embeddings
        ]
        return distances

    def indices_of_nearest_neighbors_from_distances(
        self,
        distances: List[float],
        n: int = 5
    ) -> List[int]:
        return sorted(range(len(distances)), key=lambda i: distances[i])[:n]

    async def search_similar_chunks(
        self,
        query: str,
        all_embeddings: List[List[float]],
        all_chunks: List[str],
        n: int = 5
    ) -> List[Tuple[str, float]]:
        query_embedding = await self.generate_embedding(query)
        distances = self.distances_from_embeddings(query_embedding, all_embeddings)
        nearest_indices = self.indices_of_nearest_neighbors_from_distances(distances, n)
        
        return [(all_chunks[i], distances[i]) for i in nearest_indices]

    async def cleanup(self):
        if self.http_client:
            await self.http_client.aclose()

async def main(text):
    agent = EmbeddingAgent()
    await agent.initialize()
    
    embedding = await agent.generate_embedding(text)
    
    await agent.cleanup()
    
    return json.dumps({"embedding": embedding})

if __name__ == "__main__":
    input_text = sys.argv[1]
    result = asyncio.run(main(input_text))
    print(result)