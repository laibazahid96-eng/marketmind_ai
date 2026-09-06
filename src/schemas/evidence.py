from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class ClaimType(str, Enum):
    FACT = "fact"
    INFERENCE = "inference"
    RECOMMENDATION = "recommendation"
    UNCERTAINTY = "uncertainty"

class SourceKind(str, Enum):
    RETRIEVED_DOCUMENT = "retrieved_document"
    SEARCH_RESULT = "search_result"
    CALCULATION = "calculation"
    MODEL_GENERATED = "model_generated"

class CredibilityRating(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class EvidenceRecord(BaseModel):
    evidence_id: str = Field(description="Unique identifier, e.g., 'EVD-0042'")
    question_id: str = Field(description="Target SubQuestion ID, e.g., 'SQ-1.1'")
    claim: str = Field(description="Atomic claim extracted from tool output")
    claim_type: ClaimType
    source_ref: str = Field(description="Must match a valid ToolResult ID")
    source_kind: SourceKind
    source_detail: str
    credibility: CredibilityRating
    recency: str
    corroborating_evidence_ids: List[str] = Field(default_factory=list)
    confidence: CredibilityRating
    analyst_notes: Optional[str] = None