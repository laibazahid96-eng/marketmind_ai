from src.tools.registry import calculate_metric, search_information
from src.schemas.models import EvidenceRecord

def test_growth_rate():
    x = calculate_metric("growth_rate", [100, 125])
    assert round(x["result"], 3) == 0.25

def test_search():
    x = search_information("AI customer support", max_results=5)
    assert len(x["hits"]) > 0

def test_evidence_schema():
    e = EvidenceRecord(
        evidence_id="E001", question_id="Q1", claim="A sourced claim",
        claim_type="fact", source_ref="R1", source_kind="search_result",
        source_detail="fixture", credibility="medium", recency="known",
        confidence="medium", analyst_notes="checked"
    )
    assert e.claim_type == "fact"
