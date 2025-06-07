import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

def generate_kpis(department):
    today = datetime.now().date()
    if department == "Sales":
        return {
            "Total Sales": f"₹{random.randint(800000, 1200000):,}",
            "Open Orders": random.randint(10, 30),
            "Leads Created": random.randint(5, 15),
            "Conversion Rate": f"{random.uniform(0.18, 0.33):.2%}"
        }
    elif department == "Inventory":
        return {
            "Stock Items": random.randint(28, 35),
            "Low Stock": random.randint(2, 7),
            "Valuation": f"₹{random.randint(300000, 800000):,}",
            "Recent Movements": random.randint(15, 40)
        }
    elif department == "Accounts":
        return {
            "Unpaid Invoices": random.randint(5, 15),
            "Revenue (Month)": f"₹{random.randint(200000, 500000):,}",
            "Overdue Invoices": random.randint(1, 5),
            "Avg Payment Delay": f"{random.randint(1, 14)} days"
        }
    elif department == "HR":
        return {
            "Active Employees": random.randint(25, 35),
            "On Leave": random.randint(2, 6),
            "New Hires": random.randint(0, 2),
            "Headcount": random.randint(25, 35)
        }
    elif department == "Management":
        return {
            "Net Profit": f"₹{random.randint(40000, 100000):,}",
            "Revenue": f"₹{random.randint(800000, 1200000):,}",
            "Expenses": f"₹{random.randint(400000, 800000):,}",
            "Growth Rate": f"{random.uniform(0.02, 0.17):.2%}"
        }
    else:
        return {}

def get_analytics_df(department):
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(30)][::-1]
    if department == "Sales":
        vals = [random.randint(25000, 50000) for _ in range(30)]
        label = "Daily Sales"
    elif department == "Inventory":
        vals = [random.randint(200, 400) for _ in range(30)]
        label = "Stock Movements"
    elif department == "Accounts":
        vals = [random.randint(8000, 20000) for _ in range(30)]
        label = "Daily Revenue"
    elif department == "HR":
        vals = [random.randint(0, 3) for _ in range(30)]
        label = "New Hires"
    elif department == "Management":
        vals = [random.randint(80000, 200000) for _ in range(30)]
        label = "Revenue"
    else:
        vals = [random.randint(100, 200) for _ in range(30)]
        label = "Metric"
    df = pd.DataFrame({"Date": dates, label: vals})
    return df

def show_analytics_dashboard(department="Sales"):
    st.subheader(f"{department} KPIs")
    kpis = generate_kpis(department)
    col_list = st.columns(len(kpis))
    for i, (k, v) in enumerate(kpis.items()):
        col_list[i].metric(k, v)
    st.divider()
    st.subheader(f"{department} Trends")
    df = get_analytics_df(department)
    label = df.columns[1]
    fig = px.line(df, x="Date", y=label, markers=True, title=f"{label} (Last 30 Days)")
    st.plotly_chart(fig, use_container_width=True)