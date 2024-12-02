# azure_language_service.py
import asyncio
import json
import sys
import logging

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.textanalytics import TextAnalyticsClient
    azure_sdk_available = True
except ImportError:
    azure_sdk_available = False

from config.config import Config

logger = logging.getLogger(__name__)

class AzureLanguageService:
    def __init__(self):
        self.client = None

    async def initialize(self):
        if not azure_sdk_available:
            logger.error("Azure SDK is not installed. AzureLanguageService cannot be initialized.")
            return
        config = Config()
        if not config.AZURE_LANGUAGE_SERVICE_ENDPOINT or not config.AZURE_LANGUAGE_SERVICE_API_KEY:
            logger.error("AZURE_LANGUAGE_SERVICE_ENDPOINT or AZURE_LANGUAGE_SERVICE_API_KEY not set. AzureLanguageService cannot be initialized.")
            return
        try:
            self.client = TextAnalyticsClient(
                endpoint=config.AZURE_LANGUAGE_SERVICE_ENDPOINT,
                credential=AzureKeyCredential(str(config.AZURE_LANGUAGE_SERVICE_API_KEY))
            )
            logger.info("AzureLanguageService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AzureLanguageService: {str(e)}")
            raise

    async def generate_summary(self, text: str) -> str:
        try:
            poller = self.client.begin_extract_summary([text])
            extract_summary_results = poller.result()
            for result in extract_summary_results:
                if result.kind == "ExtractiveSummarization":
                    return " ".join([sentence.text for sentence in result.sentences])
            return ""
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return ""

    async def detect_language(self, text: str) -> str:
        try:
            result = self.client.detect_language([text])[0]
            return result.primary_language.name
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "Unknown"

    async def recognize_entities(self, text: str) -> list:
        try:
            result = self.client.recognize_entities([text])[0]
            return [{"text": entity.text, "category": entity.category, "confidence_score": entity.confidence_score}
                    for entity in result.entities]
        except Exception as e:
            logger.error(f"Error recognizing entities: {str(e)}")
            return []

    async def extract_key_phrases(self, text: str) -> list:
        try:
            result = self.client.extract_key_phrases([text])[0]
            return result.key_phrases
        except Exception as e:
            logger.error(f"Error extracting key phrases: {str(e)}")
            return []

    async def cleanup(self):
        if self.client:
            self.client = None
        logger.info("AzureLanguageService cleanup completed.")

async def main(text):
    service = AzureLanguageService()
    await service.initialize()
    
    summary = await service.generate_summary(text)
    language = await service.detect_language(text)
    entities = await service.recognize_entities(text)
    key_phrases = await service.extract_key_phrases(text)
    
    await service.cleanup()
    
    return json.dumps({
        "summary": summary,
        "language": language,
        "entities": entities,
        "key_phrases": key_phrases
    })

if __name__ == "__main__":
    input_text = sys.argv[1]
    result = asyncio.run(main(input_text))
    print(result)