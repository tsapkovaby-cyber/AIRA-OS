import json


class StructuredOutputValidator:
    """Small dependency-free validator for required fields and JSON primitive types."""
    TYPES = {"object": dict, "array": list, "string": str, "number": (int, float), "integer": int, "boolean": bool}

    def validate(self, raw, schema):
        try:
            value = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSON output") from exc
        expected = self.TYPES.get(schema.get("type"))
        if expected and not isinstance(value, expected):
            raise ValueError("output has wrong type")
        for field in schema.get("required", []):
            if not isinstance(value, dict) or field not in value:
                raise ValueError(f"missing required field: {field}")
        for field, spec in schema.get("properties", {}).items():
            if isinstance(value, dict) and field in value and spec.get("type") in self.TYPES and not isinstance(value[field], self.TYPES[spec["type"]]):
                raise ValueError(f"wrong type for field: {field}")
        return value
