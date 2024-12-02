# llama3_llm.py
import asyncio
import json
import sys
import aiohttp
from config.config import Config
import logging

logger = logging.getLogger(__name__)

class Llama3LLM:
    def __init__(self):
        self.config = Config()
        self.endpoint = self.config.META_LLAMA_CHAT_ENDPOINT
        self.api_key = self.config.META_LLAMA_API_KEY
        self.session = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        if self.session:
            await self.session.close()
        logger.info("Llama3LLM cleanup completed.")

    async def generate_response(self, prompt: str, max_tokens: int = 2000):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        # Format the prompt according to Llama 3.1 specifications
        formatted_prompt = f"{prompt}"
        data = {
            "prompt": formatted_prompt,
            "temperature": 0.7,
            "max_tokens": max_tokens,
            "stop": ["\n", "\n"]  # Stop generation at these tokens
        }
        try:
            async with self.session.post(self.endpoint, json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"API call failed: {response.status} - {error_text}")
                result = await response.json()
                # Extract the generated text
                generated_text = result.get("choices", [{}])[0].get("text", "")
                # Remove any trailing stop tokens
                for stop_token in ["\n", "\n"]:
                    generated_text = generated_text.replace(stop_token, "").strip()
                return generated_text
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise

    async def chat(self, messages: list, max_tokens: int = 2000):
        """
        Handle a conversation with multiple messages.
        :param messages: List of message dictionaries with 'role' and 'content' keys
        :param max_tokens: Maximum number of tokens to generate
        :return: The model's response
        """
        formatted_prompt = ""
        for message in messages:
            role = message['role']
            content = message['content']
            formatted_prompt += f"{role} {content} "
        formatted_prompt += "assistant"
        return await self.generate_response(formatted_prompt, max_tokens)

async def main(action, *args):
    llm = Llama3LLM()
    await llm.initialize()
    
    result = None
    if action == "generate":
        result = await llm.generate_response(args[0], int(args[1]) if len(args) > 1 else 2000)
    elif action == "chat":
        messages = json.loads(args[0])
        max_tokens = int(args[1]) if len(args) > 1 else 2000
        result = await llm.chat(messages, max_tokens)
    
    await llm.cleanup()
    
    return json.dumps({"result": result})

if __name__ == "__main__":
    action = sys.argv[1]
    args = sys.argv[2:]
    result = asyncio.run(main(action, *args))
    print(result)