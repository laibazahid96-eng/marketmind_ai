from dataclasses import dataclass, field

# Conservative configurable estimate for the cost dashboard.
# Exact billing can vary by model/account; the UI labels this as an estimate.
INPUT_PER_M = 0.20
OUTPUT_PER_M = 1.20

@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    by_stage: dict = field(default_factory=dict)

    def add(self, stage: str, usage: dict):
        self.input_tokens += usage.get("input_tokens", 0)
        self.output_tokens += usage.get("output_tokens", 0)
        self.calls += 1
        s = self.by_stage.setdefault(stage, {"input_tokens": 0, "output_tokens": 0, "calls": 0})
        s["input_tokens"] += usage.get("input_tokens", 0)
        s["output_tokens"] += usage.get("output_tokens", 0)
        s["calls"] += 1

    @property
    def estimated_cost(self):
        return (self.input_tokens / 1_000_000) * INPUT_PER_M + (self.output_tokens / 1_000_000) * OUTPUT_PER_M
