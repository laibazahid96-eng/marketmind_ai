import time
import os
from typing import Any, Dict, List, Type, Optional
import openai
from pydantic import BaseModel

PRICE_PER_1K_INPUT = {"gpt-4o": 0.0025, "gpt-4o-mini": 0.00015}
PRICE_PER_1K_OUTPUT = {"gpt-4o": 0.0100, "gpt-4o-mini": 0.00060}

class ReliableLLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def call_chat(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        temperature: float = 0.2,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_retries: int = 3,
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        retries = 0
        backoff = 2.0
        while True:
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "timeout": timeout
                }
                if tools:
                    kwargs["tools"] = tools

                response = self.client.chat.completions.create(**kwargs)
                
                usage = response.usage
                in_cost = (usage.prompt_tokens / 1000) * PRICE_PER_1K_INPUT.get(model, 0.0025)
                out_cost = (usage.completion_tokens / 1000) * PRICE_PER_1K_OUTPUT.get(model, 0.0100)
                
                return {
                    "response": response,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "cost_usd": in_cost + out_cost
                }

            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
                retries += 1
                if retries > max_retries:
                    raise e
                time.sleep(backoff)
                backoff *= 2.0

    def call_structured(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        response_format: Type[BaseModel],
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=response_format,
            temperature=temperature
        )
        usage = response.usage
        in_cost = (usage.prompt_tokens / 1000) * PRICE_PER_1K_INPUT.get(model, 0.0025)
        out_cost = (usage.completion_tokens / 1000) * PRICE_PER_1K_OUTPUT.get(model, 0.0100)
        
        return {
            "parsed": response.choices[0].message.parsed,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "cost_usd": in_cost + out_cost
        }