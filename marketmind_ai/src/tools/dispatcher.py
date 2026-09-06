import json
import uuid
from typing import Callable, Dict, Any, List, Type
from pydantic import BaseModel, ValidationError

class ToolRegistration(BaseModel):
    name: str
    description: str
    argument_schema: Type[BaseModel]
    handler: Callable
    permission_level: str  # read, compute, write
    max_budget_calls: int = 10

class ToolDispatcher:
    def __init__(self):
        self.registry: Dict[str, ToolRegistration] = {}
        self.call_counts: Dict[str, int] = {}

    def register_tool(self, registration: ToolRegistration):
        self.registry[registration.name] = registration
        self.call_counts[registration.name] = 0

    def get_openai_tool_schemas(self) -> List[Dict[str, Any]]:
        schemas = []
        for reg in self.registry.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": reg.name,
                    "description": reg.description,
                    "parameters": reg.argument_schema.model_json_schema()
                }
            })
        return schemas

    def dispatch(self, tool_name: str, raw_arguments_json: str) -> Dict[str, Any]:
        result_id = f"TR-{uuid.uuid4().hex[:8]}"

        # 1. Resolve Tool
        if tool_name not in self.registry:
            return {
                "result_id": result_id,
                "status": "error",
                "error": f"Tool '{tool_name}' is not registered. Valid tools: {list(self.registry.keys())}"
            }

        tool = self.registry[tool_name]

        # 2. Check Call Budget
        if self.call_counts[tool_name] >= tool.max_budget_calls:
            return {
                "result_id": result_id,
                "status": "error",
                "error": f"Execution budget exhausted for tool '{tool_name}'."
            }

        # 3. Parse & Validate Schema
        try:
            parsed_json = json.loads(raw_arguments_json)
            validated_args = tool.argument_schema.model_validate(parsed_json)
        except json.JSONDecodeError:
            return {
                "result_id": result_id,
                "status": "error",
                "error": "Arguments failed to parse as valid JSON."
            }
        except ValidationError as ve:
            return {
                "result_id": result_id,
                "status": "error",
                "error": f"Schema validation failed: {ve.errors()}"
            }

        # 4. Execute Handler & Normalize Outcome
        try:
            self.call_counts[tool_name] += 1
            execution_output = tool.handler(validated_args)
            return {
                "result_id": result_id,
                "status": "success",
                "output": execution_output
            }
        except Exception as ex:
            return {
                "result_id": result_id,
                "status": "error",
                "error": f"Runtime error during tool execution: {str(ex)}"
            }