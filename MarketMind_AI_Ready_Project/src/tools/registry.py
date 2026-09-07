import json
from pathlib import Path
from typing import Callable

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "corpus.json"

def load_corpus():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def search_information(query: str, source_type: str = "all", max_results: int = 8, recency_window: str = "any"):
    corpus = load_corpus()
    terms = [t.lower() for t in query.split() if len(t) > 2]
    hits = []
    for doc in corpus:
        blob = (doc["title"] + " " + doc["text"] + " " + " ".join(doc.get("tags", []))).lower()
        score = sum(1 for t in terms if t in blob)
        if score:
            hits.append({
                "id": doc["id"], "title": doc["title"], "source_identifier": doc["source"],
                "date": doc.get("date"), "snippet": doc["text"][:500], "score": score
            })
    hits.sort(key=lambda x: x["score"], reverse=True)
    return {"hits": hits[:max(1, min(max_results, 20))]}

def retrieve_document(document_id: str, section: str = ""):
    for doc in load_corpus():
        if doc["id"] == document_id:
            return {"document": doc}
    return {"error": "document_id does not exist in the approved local corpus"}

def calculate_metric(operation: str, values: list[float], period: str = ""):
    if not values:
        return {"error": "values cannot be empty"}
    if operation == "average":
        result = sum(values) / len(values)
        formula = "sum(values) / len(values)"
    elif operation == "ratio":
        if len(values) != 2 or values[1] == 0:
            return {"error": "ratio requires exactly two values and denominator != 0"}
        result = values[0] / values[1]
        formula = "numerator / denominator"
    elif operation == "growth_rate":
        if len(values) != 2 or values[0] == 0:
            return {"error": "growth_rate requires [old, new] and old != 0"}
        result = (values[1] - values[0]) / values[0]
        formula = "(new - old) / old"
    elif operation == "cagr":
        if len(values) != 3 or values[0] <= 0 or values[1] <= 0 or values[2] <= 0:
            return {"error": "cagr requires [start, end, years] with positive values"}
        result = (values[1] / values[0]) ** (1 / values[2]) - 1
        formula = "(end / start) ** (1 / years) - 1"
    else:
        return {"error": "unsupported operation"}
    return {"result": result, "formula": formula, "inputs": values, "period": period}

def compare_companies(entities: list[str], attributes: list[str], evidence: list[dict]):
    matrix = {}
    for e in entities[:8]:
        matrix[e] = {}
        for a in attributes[:8]:
            matches = [x for x in evidence if e.lower() in x.get("claim","").lower() and a.lower() in x.get("claim","").lower()]
            matrix[e][a] = {"value": matches[0]["claim"] if matches else "not established",
                            "evidence_ids": [m["evidence_id"] for m in matches]}
    return {"matrix": matrix}

def save_research(question_id: str, claim: str, claim_type: str, source_ref: str, confidence: str, evidence_store: list, tool_history: list):
    valid_refs = {x.get("result_id") for x in tool_history if x.get("result_id")}
    if source_ref not in valid_refs:
        return {"error": "source_ref does not resolve to a prior tool result; evidence rejected"}
    eid = f"E{len(evidence_store)+1:03d}"
    rec = {
        "evidence_id": eid, "question_id": question_id, "claim": claim,
        "claim_type": claim_type, "source_ref": source_ref,
        "source_kind": "search_result", "source_detail": source_ref,
        "credibility": "medium", "recency": "known",
        "corroboration": [], "confidence": confidence,
        "analyst_notes": "Stored only after source_ref resolution."
    }
    evidence_store.append(rec)
    return {"evidence": rec}

def generate_report(run_id: str, sections=None):
    return {"run_id": run_id, "status": "assembled_from_state"}

TOOL_SPECS = {
    "search_information": {
        "permission": "read",
        "description": "Search the approved deterministic local research corpus. Use for factual source discovery. Never treat model knowledge as evidence.",
        "parameters": {"type":"object","properties":{
            "query":{"type":"string","minLength":3,"maxLength":300},
            "source_type":{"type":"string","enum":["all","vendor","press","pricing"]},
            "max_results":{"type":"integer","minimum":1,"maximum":20},
            "recency_window":{"type":"string","enum":["1y","3y","5y","any"]}
        },"required":["query"],"additionalProperties":False}
    },
    "retrieve_document": {
        "permission": "read",
        "description": "Retrieve a document only when its exact id exists in the approved corpus.",
        "parameters": {"type":"object","properties":{
            "document_id":{"type":"string","minLength":1,"maxLength":80},
            "section":{"type":"string","maxLength":100}
        },"required":["document_id"],"additionalProperties":False}
    },
    "calculate_metric": {
        "permission": "compute",
        "description": "Perform deterministic arithmetic in Python.",
        "parameters": {"type":"object","properties":{
            "operation":{"type":"string","enum":["growth_rate","cagr","ratio","average"]},
            "values":{"type":"array","items":{"type":"number"},"minItems":1,"maxItems":5},
            "period":{"type":"string","maxLength":50}
        },"required":["operation","values"],"additionalProperties":False}
    },
    "compare_companies": {
        "permission": "compute",
        "description": "Build a comparison matrix from the current evidence store only. Unknown cells remain not established.",
        "parameters": {"type":"object","properties":{
            "entities":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":8},
            "attributes":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":8}
        },"required":["entities","attributes"],"additionalProperties":False}
    },
    "save_research": {
        "permission": "write",
        "description": "Save one evidence claim only when source_ref resolves to a prior tool result.",
        "parameters": {"type":"object","properties":{
            "question_id":{"type":"string","minLength":1,"maxLength":40},
            "claim":{"type":"string","minLength":5,"maxLength":500},
            "claim_type":{"type":"string","enum":["fact","inference","recommendation","uncertainty"]},
            "source_ref":{"type":"string","minLength":1,"maxLength":80},
            "confidence":{"type":"string","enum":["high","medium","low"]}
        },"required":["question_id","claim","claim_type","source_ref","confidence"],"additionalProperties":False}
    },
    "generate_report": {
        "permission": "write",
        "description": "Assemble a report from stored state. The UI approval gate controls publication.",
        "parameters": {"type":"object","properties":{
            "run_id":{"type":"string","minLength":1,"maxLength":80},
            "sections":{"type":"array","items":{"type":"string"},"maxItems":10}
        },"required":["run_id"],"additionalProperties":False}
    },
}

def openai_tools():
    return [{"type":"function","name":name,"description":spec["description"],
             "parameters":spec["parameters"],"strict":True} for name,spec in TOOL_SPECS.items()]

def handler(name: str):
    return {
        "search_information": search_information,
        "retrieve_document": retrieve_document,
        "calculate_metric": calculate_metric,
        "compare_companies": compare_companies,
        "save_research": save_research,
        "generate_report": generate_report,
    }[name]
