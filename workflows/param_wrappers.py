import inspect
import json
# workflows/param_wrappers.py
import re

def tool_with_named_args(func):
    def wrapper(input_str: str):
        params = {}
        pattern = r'(\w+)=("[^"]+"|[^,]+)'
        matches = re.findall(pattern, input_str)
        
        for key, value in matches:
            # Clean and convert values
            value = value.strip().strip('"')
        
            if '=' in value:
                value = value.split('=')[-1].strip()
            
            
            if re.match(r'^-?\d+(\.\d+)?$', value):
                params[key] = float(value)
            else:
                params[key] = value
        
        return func(**params)
    return wrapper
    def wrapper(input_data):

        if isinstance(input_data, dict):
            return func(**input_data)
            
    
        if isinstance(input_data, str):
            try:
                input_json = json.loads(input_data)
                if isinstance(input_json, dict):
                    return func(**input_json)
                elif isinstance(input_json, list):
                    return func(*input_json)
            except json.JSONDecodeError:
        
                pass
            except Exception:
                pass

    
        if isinstance(input_data, str) and "," in input_data:
            values = [x.strip() for x in input_data.split(",")]
            params = list(inspect.signature(func).parameters.keys())
            args = {k: v for k, v in zip(params, values)}
            return func(**args)
            

        if isinstance(input_data, str):
            pattern = r'(\w+)\s*=\s*([^,]+)'
            matches = re.findall(pattern, input_data)
            if matches:
                args = {k: v.strip('\'" ') for k, v in matches}
                return func(**args)

    
        if isinstance(input_data, str):
            params = list(inspect.signature(func).parameters.keys())
            if params:
                return func(**{params[0]: input_data})
                

        return func(input_data)
    return wrapper