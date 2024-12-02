# File: tests/unit/test_llama3_llm.py

import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.llama3_llm import Llama3LLM, Llama3Config
from config.config import config
import aiohttp

@pytest.fixture
def llama3_config():
    return Llama3Config(
        endpoint=config.LLAMA3_API_ENDPOINT,
        api_key=config.LLAMA3_API_KEY
    )

@pytest.fixture
async def mock_session():
    async with aiohttp.ClientSession() as session:
        yield session

@pytest.fixture
async def llama3_llm(llama3_config, mock_session):
    llama3 = Llama3LLM(llama3_config)
    llama3.session = mock_session
    return llama3

@pytest.mark.asyncio
async def test_acall(llama3_llm, mocker):
    prompt = "Test prompt"
    expected_response = "Test response"

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": expected_response}}]}
    mock_response.text.return_value = "Test response text"
    mock_post = mocker.patch.object(llama3_llm.session, 'post', return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()))

    result = await llama3_llm._acall(prompt)

    assert result == expected_response
    mock_post.assert_called_once() 

@pytest.mark.asyncio
async def test_agenerate(llama3_llm, mocker):
    prompts = ["Prompt 1", "Prompt 2"]
    expected_responses = ["Response 1", "Response 2"]

    mock_responses = [
        AsyncMock(
            status=200,
            json=AsyncMock(return_value={"choices": [{"message": {"content": resp}}]}),
            text=AsyncMock(return_value="Test response text")
        )
        for resp in expected_responses
    ]
    mock_post = mocker.patch.object(llama3_llm.session, 'post', side_effect=[
        AsyncMock(__aenter__=AsyncMock(return_value=mock_responses[i]), __aexit__=AsyncMock())
        for i in range(len(prompts))
    ])

    results = await llama3_llm._agenerate(prompts)

    assert results == expected_responses
    assert mock_post.call_count == len(prompts)