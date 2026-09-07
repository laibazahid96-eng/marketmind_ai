from dataclasses import dataclass
import os

@dataclass
class Settings:
    model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "8"))
    max_tool_calls: int = int(os.getenv("MAX_TOOL_CALLS", "20"))
    max_repair_rounds: int = int(os.getenv("MAX_REPAIR_ROUNDS", "2"))
    max_budget_usd: float = float(os.getenv("MAX_BUDGET_USD", "0.50"))
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "60"))

settings = Settings()
