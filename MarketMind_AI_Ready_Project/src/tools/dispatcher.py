import json, time, uuid
from jsonschema import validate, ValidationError
from .registry import TOOL_SPECS, handler

class Dispatcher:
    def __init__(self, state, max_calls=20):
        self.state = state
        self.max_calls = max_calls

    def dispatch(self, name, arguments):
        result_id = "R" + uuid.uuid4().hex[:8]
        entry = {"result_id": result_id, "tool": name, "arguments": arguments, "timestamp": time.time()}
        try:
            if name not in TOOL_SPECS:
                result = {"error": f"unknown tool: {name}"}
            elif len(self.state.tool_history) >= self.max_calls:
                result = {"error": "tool call budget exhausted"}
            else:
                spec = TOOL_SPECS[name]
                validate(instance=arguments, schema=spec["parameters"])
                fn = handler(name)
                if name == "save_research":
                    result = fn(**arguments, evidence_store=self.state.evidence, tool_history=self.state.tool_history)
                elif name == "compare_companies":
                    result = fn(**arguments, evidence=self.state.evidence)
                else:
                    result = fn(**arguments)
        except ValidationError as e:
            result = {"error": f"schema validation failed: {e.message}"}
        except Exception as e:
            result = {"error": f"tool execution failed: {e}"}
        entry["result"] = result
        self.state.tool_history.append(entry)
        return result_id, result
