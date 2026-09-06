from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from src.schemas.evidence import ClaimType, EvidenceRecord

class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    EXPAND = "expand"
    RESCOPE = "rescope"

class Finding(BaseModel):
    statement: str
    claim_type: ClaimType
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: str

class MatrixCell(BaseModel):
    value: str
    is_established: bool
    evidence_ids: List[str] = Field(default_factory=list)

class ApprovalRecord(BaseModel):
    approver_id: str
    decision: ApprovalDecision
    timestamp: str
    notes: Optional[str] = None

class MarketIntelligenceReport(BaseModel):
    report_id: str
    generated_at: str
    model_versions: Dict[str, str]
    total_run_cost_usd: float
    research_objective: str
    assumptions: List[str]
    executive_summary: str
    market_overview: List[Finding]
    key_trends: List[Finding]
    competitor_analysis_matrix: Dict[str, Dict[str, MatrixCell]]
    opportunities: List[Finding]
    risks: List[Finding]
    limitations_and_gaps: List[str]
    evidence_appendix: List[EvidenceRecord]
    approval: Optional[ApprovalRecord] = None