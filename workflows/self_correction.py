import inspect
import json
from langchain_openai import ChatOpenAI
import os

class SelfCorrectionSystem:
    @staticmethod
    def correct(operation_name: str, params: dict, error_message: str) -> dict:
        llm = ChatOpenAI(
            openai_api_key=os.getenv("TOGETHER_API_KEY"),
            openai_api_base="https://api.together.xyz/v1",
            model="meta-llama/Llama-3-70b-chat-hf",
            temperature=0.3,
            max_tokens=256,
        )
        prompt = f"""
ERP operation '{operation_name}' failed with error: {error_message}
Parameters used: {params}

Analyze the error and suggest corrected parameters in JSON format.
Output only the corrected JSON parameters, no other text.
"""
        try:
            response = llm.invoke(prompt)
            corrected_params = json.loads(response.content)
            return corrected_params
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error: {str(e)}")
            return None
        except Exception as e:
            print(f"⚠️ LLM invocation error: {str(e)}")
            return None

def correct_parameters(func, params: dict) -> dict:
    sig = inspect.signature(func)
    valid_params = {}
    for name, param in sig.parameters.items():
        if name in params:
            valid_params[name] = params[name]
        elif param.default != param.empty:
            valid_params[name] = param.default
        else:
            prompt = f"""
Function '{func.__name__}' requires parameter '{name}' of type {param.annotation}.
Generate appropriate value based on context: {params}
Output only the value, no other text.
"""
            llm = ChatOpenAI(
                openai_api_key=os.getenv("TOGETHER_API_KEY"),
                openai_api_base="https://api.together.xyz/v1",
                model="meta-llama/Llama-3-70b-chat-hf",
                temperature=0.3,
                max_tokens=64,
            )
            try:
                response = llm.invoke(prompt)
                valid_params[name] = response.content
            except Exception as e:
                print(f"⚠️ Parameter generation error for '{name}': {str(e)}")
                valid_params[name] = None
    return valid_params