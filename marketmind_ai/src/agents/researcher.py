import json
from typing import Dict, Any
from src.llm.client import ReliableLLMClient
from src.tools.dispatcher import ToolDispatcher
from src.schemas.evidence import EvidenceRecord, ClaimType, SourceKind, CredibilityRating

class AutonomousResearchLoop:
    def __init__(
        self,
        llm_client: ReliableLLMClient,
        dispatcher: ToolDispatcher,
        max_iterations: int = 10,
        cost_ceiling_usd: float = 2.0
    ):
        self.client = llm_client
        self.dispatcher = dispatcher
        self.max_iterations = max_iterations
        self.cost_ceiling_usd = cost_ceiling_usd

    def execute_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        state = {
            "accumulated_cost": 0.0,
            "evidence_store": [],
            "tool_history": [],
            "status": "IN_PROGRESS",
            "iterations": 0
        }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an Autonomous Business Research Agent. Execute the provided research plan "
                    "by invoking tools. Store findings with explicitly cited evidence. "
                    "Stop when all sub-questions are satisfied or no further progress can be made."
                )
            },
            {"role": "user", "content": f"Research Plan:\n{json.dumps(plan_data, indent=2)}"}
        ]

        stuck_detector = set()

        while state["iterations"] < self.max_iterations:
            if state["accumulated_cost"] >= self.cost_ceiling_usd:
                state["status"] = "PARTIAL_COST_CEILING_REACHED"
                break

            state["iterations"] += 1

            res = self.client.call_chat(
                model="gpt-4o",
                messages=messages,
                tools=self.dispatcher.get_openai_tool_schemas(),
                temperature=0.2
            )
            state["accumulated_cost"] += res["cost_usd"]
            response_msg = res["response"].choices[0].message

            if response_msg.tool_calls:
                messages.append(response_msg)
                
                for tcall in response_msg.tool_calls:
                    call_sig = f"{tcall.function.name}:{tcall.function.arguments}"
                    
                    if call_sig in stuck_detector:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tcall.id,
                            "content": json.dumps({"error": "STUCK_LOOP_DETECTED: Identical call repeated. Change parameters or abandon question."})
                        })
                        continue
                    
                    stuck_detector.add(call_sig)

                    disp_result = self.dispatcher.dispatch(
                        tool_name=tcall.function.name,
                        raw_arguments_json=tcall.function.arguments
                    )
                    
                    if tcall.function.name == "save_research" and disp_result["status"] == "success":
                        record = EvidenceRecord(
                            evidence_id=f"EVD-{len(state['evidence_store'])+1:04d}",
                            question_id=disp_result["output"].get("question_id", "SQ-GENERIC"),
                            claim=disp_result["output"]["claim"],
                            claim_type=ClaimType(disp_result["output"]["claim_type"]),
                            source_ref=disp_result["result_id"],
                            source_kind=SourceKind.RETRIEVED_DOCUMENT,
                            source_detail=disp_result["output"].get("source_detail", "Corpus"),
                            credibility=CredibilityRating.HIGH,
                            recency="2026",
                            confidence=CredibilityRating.HIGH
                        )
                        state["evidence_store"].append(record)

                    state["tool_history"].append({
                        "call": tcall.function.name,
                        "args": tcall.function.arguments,
                        "result_id": disp_result["result_id"]
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tcall.id,
                        "content": json.dumps(disp_result)
                    })
            else:
                state["status"] = "COMPLETED"
                break

        if state["iterations"] >= self.max_iterations and state["status"] == "IN_PROGRESS":
            state["status"] = "PARTIAL_MAX_ITERATIONS_EXCEEDED"

        return state