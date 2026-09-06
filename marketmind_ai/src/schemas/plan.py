from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class EvidenceType(str, Enum):
    FINANCIAL_FILING = "financial_filing"
    PRICING_PAGE = "pricing_page"
    PRODUCT_DOCS = "product_docs"
    PRESS_RELEASE = "press_release"
    ANALYST_REPORT = "analyst_report"

class CandidateTool(str, Enum):
    SEARCH_INFO = "search_information"
    RETRIEVE_DOC = "retrieve_document"
    CALCULATE_METRIC = "calculate_metric"
    COMPARE_COMPANIES = "compare_companies"

class SubQuestion(BaseModel):
    id: str = Field(description="Unique ID, e.g., 'SQ-1.1'")
    question: str = Field(description="Specific, answerable question")
    evidence_type: EvidenceType
    candidate_tools: List[CandidateTool]
    priority: int = Field(ge=1, le=5)

class ResearchObjective(BaseModel):
    id: str = Field(description="Objective ID, e.g., 'OBJ-1'")
    title: str
    description: str
    sub_questions: List[SubQuestion]

class ResearchPlan(BaseModel):
    scope_summary: str
    assumptions: List[str]
    ambiguities_identified: List[str]
    objectives: List[ResearchObjective]