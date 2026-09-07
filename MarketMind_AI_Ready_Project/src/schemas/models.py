from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

ClaimType = Literal["fact", "inference", "recommendation", "uncertainty"]
Confidence = Literal["high", "medium", "low"]

class Scope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_type: str
    segment: str
    geography: str
    time_horizon: str
    deliverable_type: str
    ambiguities: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)

class SubQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    question: str
    required_evidence_type: str
    candidate_tools: list[Literal["search_information","retrieve_document","calculate_metric","compare_companies","save_research","generate_report"]]
    priority: Literal["high","medium","low"]

class Objective(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    sub_questions: list[SubQuestion] = Field(min_length=2, max_length=5)

class ResearchPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    objectives: list[Objective] = Field(min_length=3, max_length=6)

class EvidenceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: str
    question_id: str
    claim: str
    claim_type: ClaimType
    source_ref: str
    source_kind: Literal["retrieved_document","search_result","calculation","model_generated"]
    source_detail: str
    credibility: Literal["high","medium","low","unknown"]
    recency: str
    corroboration: list[str] = Field(default_factory=list)
    confidence: Confidence
    analyst_notes: str

class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    statement: str
    claim_type: ClaimType
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: Confidence

class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_id: str
    research_objective: str
    executive_summary: str
    market_overview: list[Finding]
    key_trends: list[Finding]
    competitor_analysis: dict
    opportunities: list[Finding]
    risks: list[Finding]
    evidence_appendix: list[EvidenceRecord]
    recommendations: list[Finding]
    confidence_level: Confidence
    rationale: str
    limitations_and_gaps: list[str]
    sources: list[str]
    approval: dict | None = None
