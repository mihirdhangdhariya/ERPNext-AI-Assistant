import streamlit as st
import pandas as pd
import ast
import re
from datetime import date

def fix_datetime_in_dict(d):
    """Convert datetime.date(x, y, z) to YYYY-MM-DD strings in dict."""
    for k, v in d.items():
        if isinstance(v, str):
            match = re.match(r"datetime\.date\((\d+), (\d+), (\d+)\)", v)
            if match:
                y, m, d_ = map(int, match.groups())
                d[k] = f"{y:04d}-{m:02d}-{d_:02d}"
    return d

def try_parse_sales_data_string(s):
    """
    Try to extract a list of dicts from a string, fixing datetime.date to ISO strings.
    """
    # Find the list part (between [ and ])
    match = re.search(r"\[.*\]", s, re.DOTALL)
    if not match:
        return None
    list_str = match.group(0)
    # Replace datetime.date(x, y, z) with "datetime.date(x, y, z)"
    list_str = re.sub(r"(datetime\.date\(\d+, \d+, \d+\))", r'"\1"', list_str)
    try:
        data = ast.literal_eval(list_str)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Fix datetime strings in dicts
            data = [fix_datetime_in_dict(d) for d in data]
            return data
    except Exception:
        pass
    return None

def dict_to_markdown_table(data):
    df = pd.DataFrame(data)
    # Convert any datetime/date columns to ISO string
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or df[col].apply(lambda x: hasattr(x, 'isoformat')).any():
            df[col] = df[col].apply(lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x))
    return df.to_markdown(index=False)

def list_to_markdown_bullets(items):
    return "\n".join([f"- {item}" for item in items])

def try_parse_list_of_dicts_from_str(result):
    try:
        parsed = ast.literal_eval(result)
        if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
            return parsed
    except Exception:
        pass
    return None

def display_agent_result(result, heading=None):
    if heading:
        st.markdown(f"### {heading}")
    
    # Handle error messages
    if isinstance(result, str) and result.startswith("⚠️"):
        st.error(result)
        return
    
    # Handle dictionary errors from operations
    if isinstance(result, dict) and 'error' in result:
        st.error(f"⚠️ {result['error']}")
        return
        
    # DataFrame
    if isinstance(result, pd.DataFrame):
        for col in result.columns:
            if pd.api.types.is_datetime64_any_dtype(result[col]) or result[col].apply(lambda x: hasattr(x, 'isoformat')).any():
                result[col] = result[col].apply(lambda x: x.isoformat() if hasattr(x, 'isoformat') else str(x))
        st.markdown(result.to_markdown(index=False), unsafe_allow_html=True)
    elif isinstance(result, list) and result and isinstance(result[0], dict):
        st.markdown(dict_to_markdown_table(result), unsafe_allow_html=True)
    elif isinstance(result, list):
        st.markdown(list_to_markdown_bullets(result), unsafe_allow_html=True)
    elif isinstance(result, dict):
        st.markdown(dict_to_markdown_table([result]), unsafe_allow_html=True)
    elif isinstance(result, str):
        # Try advanced sales data parsing!
        parsed_sales = try_parse_sales_data_string(result)
        if parsed_sales:
            st.markdown(dict_to_markdown_table(parsed_sales), unsafe_allow_html=True)
            return
        parsed = try_parse_list_of_dicts_from_str(result)
        if parsed:
            st.markdown(dict_to_markdown_table(parsed), unsafe_allow_html=True)
        else:
            st.markdown(str(result))
    else:
        st.markdown(str(result))