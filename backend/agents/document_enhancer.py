# document_enhancer.py

from .azure_language_service import AzureLanguageService
from config.config import Config
import logging

logger = logging.getLogger(__name__)

class DocumentEnhancer:
    def __init__(self):
        try:
            self.language_service = AzureLanguageService()
        except Exception as e:
            logger.error(f"Error creating AzureLanguageService: {str(e)}")
            raise

    async def initialize(self):
        try:
            logger.info("Initializing DocumentEnhancer")
            await self.language_service.initialize()
            logger.info("DocumentEnhancer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing DocumentEnhancer: {str(e)}")
            raise

    async def enhance_document(self, document: dict) -> dict:
        try:
            enhanced_doc = document.copy()
            text = document.get('content', '')

            # Generate summary
            enhanced_doc['summary'] = await self.language_service.generate_summary(text)

            # Detect language
            enhanced_doc['language'] = await self.language_service.detect_language(text)

            # Recognize entities
            enhanced_doc['entities'] = await self.language_service.recognize_entities(text)

            # Extract key phrases
            enhanced_doc['key_phrases'] = await self.language_service.extract_key_phrases(text)

            logger.info(f"Document {document.get('id', 'unknown')} enhanced successfully")
            return enhanced_doc
        except Exception as e:
            logger.error(f"Error enhancing document: {str(e)}")
            raise

    async def process_chunk(self, chunk: dict) -> dict:
        try:
            enhanced_chunk = chunk.copy()
            text = chunk.get('content', '')

            # Generate summary for the chunk
            enhanced_chunk['summary'] = await self.language_service.generate_summary(text)

            # Extract key phrases for the chunk
            enhanced_chunk['key_phrases'] = await self.language_service.extract_key_phrases(text)

            logger.info(f"Chunk {chunk.get('id', 'unknown')} processed successfully")
            return enhanced_chunk
        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            raise

    async def cleanup(self):
        try:
            await self.language_service.cleanup()
            logger.info("DocumentEnhancer cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during DocumentEnhancer cleanup: {str(e)}")