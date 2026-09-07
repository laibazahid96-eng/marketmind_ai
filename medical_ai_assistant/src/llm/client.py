import json
import time
from typing import Any, Optional
from openai import OpenAI

class LLMError(Exception):
    pass

class LLMClient:
    def __init__(self, api_key: str, model: str, timeout: float = 60):
        if not api_key or not api_key.strip():
            raise LLMError("OpenAI API key is missing.")
        self.client = OpenAI(api_key=api_key.strip(), timeout=timeout, max_retries=0)
        self.model = model

    def responses_create(self, input_data, tools=None, temperature=None, max_output_tokens=3000):
        last_error = None
        for attempt in range(3):
            try:
                kwargs = {
                    "model": self.model,
                    "input": input_data,
                    "max_output_tokens": max_output_tokens,
                }
                if tools:
                    kwargs["tools"] = tools
                if temperature is not None:
                    # Some reasoning models may reject temperature; retry without it.
                    kwargs["temperature"] = temperature
                try:
                    response = self.client.responses.create(**kwargs)
                except Exception as e:
                    if "temperature" in str(e).lower() and "temperature" in kwargs:
                        kwargs.pop("temperature", None)
                        response = self.client.responses.create(**kwargs)
                    else:
                        raise
                return response
            except Exception as e:
                last_error = e
                msg = str(e).lower()
                transient = any(x in msg for x in ["rate limit", "timeout", "temporarily", "connection", "503", "502", "504"])
                if attempt < 2 and transient:
                    time.sleep((2 ** attempt) + 0.3 * attempt)
                    continue
                if "401" in msg or "authentication" in msg or "api key" in msg:
                    raise LLMError("OpenAI authentication failed. Check the API key in the sidebar.")
                if "quota" in msg or "billing" in msg:
                    raise LLMError("OpenAI quota/billing limit reached. Please check your API account.")
                raise LLMError(f"OpenAI request failed: {e}") from e
        raise LLMError(f"OpenAI request failed: {last_error}")

    @staticmethod
    def output_text(response) -> str:
        text = getattr(response, "output_text", None)
        return text.strip() if text else ""

    @staticmethod
    def usage(response) -> dict:
        u = getattr(response, "usage", None)
        if not u:
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        return {
            "input_tokens": int(getattr(u, "input_tokens", 0) or 0),
            "output_tokens": int(getattr(u, "output_tokens", 0) or 0),
            "total_tokens": int(getattr(u, "total_tokens", 0) or 0),
        }

    def ask_json(self, system: str, user: str, schema: dict, temperature: Optional[float] = 0.2):
        prompt = (
            system + "\n\nReturn ONLY valid JSON matching this schema. "
            "Do not add markdown fences.\nSCHEMA:\n" + json.dumps(schema) +
            "\n\nUSER REQUEST:\n" + user
        )
        response = self.responses_create(prompt, temperature=temperature, max_output_tokens=4000)
        text = self.output_text(response)
        if not text:
            raise LLMError("The model returned an empty response.")
        try:
            return json.loads(text), self.usage(response)
        except json.JSONDecodeError:
            # One bounded repair attempt.
            repair = (
                "Convert the following into ONLY valid JSON matching the supplied schema. "
                "Do not invent information.\nSCHEMA:\n" + json.dumps(schema) +
                "\nTEXT:\n" + text
            )
            response2 = self.responses_create(repair, temperature=0.0, max_output_tokens=4000)
            text2 = self.output_text(response2)
            try:
                return json.loads(text2), self.usage(response2)
            except Exception as e:
                raise LLMError("Structured output could not be parsed after one retry.") from e
