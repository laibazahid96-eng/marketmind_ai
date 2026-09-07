from dataclasses import dataclass, field, asdict
from datetime import datetime
import json, uuid

@dataclass
class ResearchState:
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    request: str = ""
    scope: dict = field(default_factory=dict)
    plan: dict = field(default_factory=dict)
    question_status: dict = field(default_factory=dict)
    evidence: list = field(default_factory=list)
    tool_history: list = field(default_factory=list)
    defects: list = field(default_factory=list)
    iteration_count: int = 0
    current_stage: str = "intake"
    incomplete: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return asdict(self)

    def save(self, directory="runs"):
        import os
        os.makedirs(f"{directory}/{self.run_id}", exist_ok=True)
        with open(f"{directory}/{self.run_id}/state.json", "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
