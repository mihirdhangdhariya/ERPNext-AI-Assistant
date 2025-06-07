from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from agents import SalesAgent, InventoryAgent, AccountsAgent, HRAgent, ManagementAgent
from analytics.dashboard import show_analytics_dashboard, get_analytics_df
import time
import pandas as pd
import os

from workflows.display_utils import display_agent_result

st.set_page_config(
    page_title="ERPNext AI Assistant",
    page_icon="🤖",
    layout="wide"
)

with st.container():
    st.markdown("### 👋 Welcome to ERP AI Assistant")
    st.write("Use the chat interface below to test various ERP modules.")

# ---- Sidebar ----
st.sidebar.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
st.sidebar.markdown("ERPNext AI Assistant")
st.sidebar.markdown("Empowering your business with actionable insights and smart automation.")

department_options = {
    "Sales": "💼 Sales",
    "Inventory": "📦 Inventory",
    "Accounts": "💰 Accounts",
    "HR": "🧑‍🤝‍🧑 HR",
    "Management": "📈 Management"
}

department_display = st.sidebar.selectbox(
    "Select Department",
    options=list(department_options.values())
)
department = next(k for k, v in department_options.items() if v == department_display)

# --- Sample Prompts/Examples ---
st.sidebar.markdown("### 📝 Sample Prompts")
sample_prompts = {
    "Sales": [
        "Show me the sales data for the last week.",
        "Create a lead for company 'Tech Innovations' with contact 'John Doe'.",
        "What are the open sales orders this month?"
    ],
    "Inventory": [
        "What are the stock levels for 'Product A'?",
        "Show me the low stock items with a threshold of 20.",
        "Update the stock for 'ITEM-30001' to 50 in the 'Main' warehouse."
    ],
    "Accounts": [
        "List the unpaid invoices for Global Tech.",
        "Record a payment of 5000 for invoice INV-50001.",
        "What is the revenue snapshot for the last month?"
    ],
    "HR": [
        "Show me the leave calendar for this week.",
        "Add a new employee named Alice Smith as an Analyst in Finance.",
        "What is the contract status for employee Alice Smith?"
    ],
    "Management": [
        "What is the sales performance for the current quarter?",
        "Give me a business snapshot overview.",
        "Generate a strategy report focusing on growth."
    ]
}
for prompt in sample_prompts[department]:
    st.sidebar.write(f"- {prompt}")

# --- "What can I ask?" Help Section ---
with st.sidebar.expander("❓ What can I ask?"):
    st.markdown("""
    - Ask for reports (e.g., "Show sales data for this month")
    - Perform operations (e.g., "Add an employee", "Update stock levels")
    - Request summaries (e.g., "Business snapshot", "Headcount report")
    - Get analytics (e.g., "Show revenue trend", "Low stock items")
    - Use natural language – the assistant understands business queries!
    """)

# ---- Onboarding Banner ----
if "onboarded" not in st.session_state:
    st.info("👋 Welcome to your ERP AI! Ask business questions, run operations, and get instant answers. Save or clear memory as needed.", icon="💡")
    st.session_state.onboarded = True

# ---- Initialize Agents ----
if "agents" not in st.session_state:
    st.session_state.agents = {
        "Sales": SalesAgent(),
        "Inventory": InventoryAgent(),
        "Accounts": AccountsAgent(),
        "HR": HRAgent(),
        "Management": ManagementAgent()
    }

# ---- Chat and Context ----
st.session_state.setdefault("messages", {})
st.session_state.setdefault("context_history", {})
st.session_state.setdefault("input_key_counter", 0)
st.session_state.messages.setdefault(department, [])
st.session_state.context_history.setdefault(department, [])

tab1, tab2 = st.tabs(["🤖 AI Assistant", "📊 Business Analytics"])

with tab1:
    st.title(f"{department_options[department]} Assistant")
    st.caption("Ask your business questions or give instructions for instant answers.")

    # Chat history
    for message in st.session_state.messages[department]:
        if message["role"] == "user":
            st.chat_message("user").markdown(f"🗣️ {message['content']}")
        else:
            st.chat_message("assistant")
            display_agent_result(message['content'])

with tab2:
    st.title("Business Analytics Dashboard")
    show_analytics_dashboard(department)

    # --- Analytics CSV Export Feature ---
    st.subheader("Export Analytics as CSV")
    analytics_df = get_analytics_df(department)
    st.download_button(
        label="⬇️ Download Analytics CSV",
        data=analytics_df.to_csv(index=False).encode(),
        file_name=f"{department}_analytics.csv",
        mime="text/csv",
        help="Export the current analytics data as a CSV file."
    )

# ---- Sidebar: Memory tools ----
with st.sidebar:
    st.divider()
    st.subheader("Memory Management")
    agent = st.session_state.agents[department]
    stats = agent.get_context_stats()
    st.caption(f"🧠 Memory: {stats['entries']} entries, {stats['vectors']} vectors")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Memory", use_container_width=True, help="Save current context to disk"):
            result = agent.save_context()
            st.toast(result)
    with col2:
        if st.button("🧹 Clear Memory", use_container_width=True, help="Clear current context"):
            result = agent.clear_context()
            st.session_state.messages[department] = []
            st.session_state.context_history[department] = []
            st.toast(result)

    with st.expander("🔍 Context Inspector"):
        if st.session_state.context_history[department]:
            st.write("**Last Context Used:**")
            last_context = st.session_state.context_history[department][-1]
            for ctx in last_context:
                st.caption(f"📅 {time.ctime(ctx['timestamp'])} | Distance: {ctx.get('distance', 'N/A')}")
                st.text(ctx['text'])
        else:
            st.info("No context used yet")

        if st.button("View All Context Entries"):
            all_entries = agent.context_manager.context_data
            if all_entries:
                df = pd.DataFrame(all_entries)[['timestamp', 'department', 'query']]
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                st.dataframe(df.sort_values('timestamp', ascending=False))
            else:
                st.warning("No context entries stored")

# ---- Chat input ----
chat_input_key = f"chat_input_{department}_{st.session_state.input_key_counter}"
prompt = st.chat_input(
    f"💬 Ask {department_options[department]} anything...",
    key=chat_input_key
)

if prompt:
    agent = st.session_state.agents[department]
    st.session_state.messages[department].append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(f"🗣️ {prompt}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        last_observation = None  # For fallback

        # Retrieve context
        context_entries = agent.context_manager.get_context(
            prompt, department, k=2
        )

        # Format context as string
        context_str = "\n\n".join(
            f"Previous Q: {entry['query']}\nPrevious A: {entry['response']}"
            for entry in context_entries
        )

        # Combine with current query
        full_query = f"{context_str}\nCurrent Question: {prompt}"

        with st.spinner("🔍 Analyzing your query..."):
            try:
                for chunk in agent.agent_executor.stream({"input": full_query}):
                    if "output" in chunk:
                        token = chunk["output"]
                        full_response += token
                        message_placeholder.markdown(f"🤖 {full_response}▌")
                    if "observation" in chunk:
                        last_observation = chunk["observation"]
                message_placeholder.empty()
                # Prefer full_response if available, otherwise use last_observation
                if full_response and full_response.strip():
                    display_agent_result(full_response)
                elif last_observation:
                    display_agent_result(last_observation)
                else:
                    st.warning("No response generated.")
                st.session_state.context_history[department].append(context_entries)
                st.toast("✅ Response generated!", icon="✅")
            except Exception as e:
                error = f"⚠️ System Error: {str(e)}"
                message_placeholder.markdown(f"🤖 {error}")
                full_response = error
                st.toast(error, icon="⚠️")

    st.session_state.messages[department].append({
        "role": "assistant", 
        "content": full_response if full_response else (last_observation or "")
    })

    if not (full_response and full_response.startswith("⚠️")):
        agent.context_manager.store_interaction(
            prompt, full_response if full_response else (last_observation or ""), department
        )

    st.session_state.input_key_counter += 1
    st.rerun()