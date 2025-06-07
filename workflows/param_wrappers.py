import inspect
import json

def tool_with_named_args(func):
    def wrapper(input_data):
        # Try to parse input_data as dict, JSON, or fallback to positional mapping.
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # If input_data is already a dict (preferred by agent)
        if isinstance(input_data, dict):
            return func(**input_data)

        # Try to parse as JSON
        if isinstance(input_data, str):
            try:
                input_json = json.loads(input_data)
                if isinstance(input_json, dict):
                    return func(**input_json)
                elif isinstance(input_json, list):
                    return func(*input_json)
            except Exception:
                pass

        # Fallback: comma-separated string
        if isinstance(input_data, str) and "," in input_data:
            values = [x.strip() for x in input_data.split(",")]
            # Map to parameters
            args = {k: v for k, v in zip(params, values)}
            return func(**args)

        # Fallback: single string as first arg
        if isinstance(input_data, str):
            return func(**{params[0]: input_data})

        # Fallback: just call with input_data
        return func(input_data)
    return wrapper