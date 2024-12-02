/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    env: {
      // Python path
      PYTHON_PATH: decodeURIComponent(process.env.PYTHON_PATH),
  
      // Azure AI Search
      AZURE_SEARCH_SERVICE_NAME: process.env.AZURE_SEARCH_SERVICE_NAME,
      AZURE_SEARCH_INDEX_NAME: process.env.AZURE_SEARCH_INDEX_NAME,
      AZURE_SEARCH_API_KEY: process.env.AZURE_SEARCH_API_KEY,
      AZURE_SEARCH_SERVICE_ENDPOINT: `https://${process.env.AZURE_SEARCH_SERVICE_NAME}.search.windows.net`,
  
      // Azure OpenAI
      AZURE_OPENAI_API_KEY: process.env.AZURE_OPENAI_API_KEY,
      AZURE_OPENAI_ENDPOINT: process.env.AZURE_OPENAI_ENDPOINT,
      AZURE_OPENAI_API_VERSION: process.env.AZURE_OPENAI_API_VERSION,
  
      // Azure OpenAI Deployments
      AZURE_OPENAI_EMBEDDING_DEPLOYMENT: process.env.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
      AZURE_OPENAI_EMBEDDING_MODEL: process.env.AZURE_OPENAI_EMBEDDING_MODEL,
      AZURE_OPENAI_EMBEDDING_DIMENSIONS: 1536,
  
      // Azure Blob Storage
      AZURE_STORAGE_CONNECTION_STRING: process.env.AZURE_STORAGE_CONNECTION_STRING,
      AZURE_STORAGE_CONTAINER_NAME: process.env.AZURE_STORAGE_CONTAINER_NAME,
      AZURE_STORAGE_API_KEY: process.env.AZURE_STORAGE_API_KEY,
  
      // Azure Language Service for Text Analytics
      AZURE_LANGUAGE_SERVICE_NAME: process.env.AZURE_LANGUAGE_SERVICE_NAME,
      AZURE_LANGUAGE_SERVICE_ENDPOINT: process.env.AZURE_LANGUAGE_SERVICE_ENDPOINT,
      AZURE_LANGUAGE_SERVICE_API_KEY: process.env.AZURE_LANGUAGE_SERVICE_API_KEY,
  
      // Azure AI Studio Project
      AZURE_AI_STUDIO_PROJECT_NAME: process.env.AZURE_AI_STUDIO_PROJECT_NAME,
  
      // Other configurations
      INDEXER_NAME: process.env.INDEXER_NAME,
      SKILLSET_NAME: process.env.SKILLSET_NAME,
      DATA_SOURCE_NAME: process.env.DATA_SOURCE_NAME,
  
      // Meta-Llama-3.1-70B-Instruct
      META_LLAMA_ENDPOINT: process.env.META_LLAMA_ENDPOINT,
      META_LLAMA_API_KEY: process.env.META_LLAMA_API_KEY,
      META_LLAMA_CHAT_ENDPOINT: `${process.env.META_LLAMA_ENDPOINT}/v1/chat/completions`,
  
      // New configuration
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    },
    async rewrites() {
      return []  // Remove the rewrite rule if you want to use Next.js API routes
    },
    // Add any other necessary configurations here
  }
  
  module.exports = nextConfig