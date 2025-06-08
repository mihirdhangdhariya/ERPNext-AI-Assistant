from datetime import datetime, timedelta
import pandas as pd
import random
import re

#  UTILITY FUNCTIONS 
def standardize_item_id(item_id: str) -> str:
    """Standardize item IDs to ITEM-XXXXX format"""
    item_id = item_id.upper().strip()
    if not item_id.startswith('ITEM-'):
        return f"ITEM-{item_id.split('-')[-1].zfill(5)}"
    parts = item_id.split('-')
    if len(parts) > 1:
        return f"ITEM-{parts[1].zfill(5)}"
    return item_id

def standardize_invoice_id(invoice_id: str) -> str:
    """Standardize invoice IDs to INV-XXXXX format"""
    invoice_id = invoice_id.upper().strip()
    if not invoice_id.startswith('INV-'):
        return f"INV-{invoice_id.split('-')[-1].zfill(5)}"
    parts = invoice_id.split('-')
    if len(parts) > 1:
        return f"INV-{parts[1].zfill(5)}"
    return invoice_id

#  GLOBAL DATA STORES 
_inventory_df = None
_invoices_df = None
_employees_df = None
_sales_orders_df = None

#  DATA INITIALIZATION 
def get_inventory():
    global _inventory_df
    if _inventory_df is None:
        _inventory_df = generate_mock_inventory(30)
    return _inventory_df

def get_invoices():
    global _invoices_df
    if _invoices_df is None:
        _invoices_df = generate_mock_invoices(30)
    return _invoices_df

def get_employees():
    global _employees_df
    if _employees_df is None:
        _employees_df = generate_mock_employees(20)
    return _employees_df

def get_sales_orders():
    global _sales_orders_df
    if _sales_orders_df is None:
        _sales_orders_df = generate_mock_sales_orders(100)
    return _sales_orders_df

#  SALES OPERATIONS 
def generate_mock_sales_orders(n=100):
    customers = ["Global Tech", "Ocean Logistics", "Skyline Industries", "MediCorp", "EduSystems", "Retail Giants", "Food Worldwide"]
    products = ["ERP License", "CRM Module", "HR Package", "Custom Development", "Support Plan", "Training Package", "Integration Service"]
    data = {
        "id": [f"SO-{10000+i}" for i in range(n)],
        "customer": random.choices(customers, k=n),
        "product": random.choices(products, k=n),
        "value": [random.randint(10000, 100000) for _ in range(n)],
        "status": random.choices(["Open", "Completed", "Cancelled"], weights=[0.4, 0.5, 0.1], k=n),
        "date": sorted([(datetime.now() - timedelta(days=random.randint(0, 180))).date() for _ in range(n)], reverse=True),
        "sales_person": [f"SP-{random.randint(100, 110)}" for _ in range(n)]
    }
    return pd.DataFrame(data)

def get_open_orders(period: str = "this month") -> pd.DataFrame:
    orders_df = get_sales_orders()
    now = datetime.now().date()
    if period == "this month":
        start_date = now.replace(day=1)
        orders = orders_df[
            (orders_df['date'] >= start_date) & 
            (orders_df['status'] == 'Open')
        ]
    elif period == "last month":
        first_day_this_month = now.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        start_date = last_day_last_month.replace(day=1)
        orders = orders_df[
            (orders_df['date'] >= start_date) &
            (orders_df['date'] <= last_day_last_month) &
            (orders_df['status'] == 'Open')
        ]
    else:
        orders = orders_df[orders_df['status'] == 'Open']
    return orders.sort_values('date', ascending=False)

def get_sales_data(period="week"):
    today = datetime.now().date()
    data = []
    for i in range(90):
        date_obj = today - timedelta(days=i)
        sales = random.randint(5000, 20000)
        data.append({"date": date_obj, "sales": sales})
    if period == "week":
        cutoff = today - timedelta(days=7)
    elif period == "month":
        cutoff = today - timedelta(days=30)
    else:
        cutoff = today - timedelta(days=365)
    filtered = [row for row in data if row["date"] >= cutoff]
    return filtered

def create_lead(company: str, contact: str, details: str = "") -> dict:
    return {
        "id": f"LD-{random.randint(20000, 29999)}",
        "company": company,
        "contact": contact,
        "details": details,
        "status": "New",
        "created_date": datetime.now(),
        "potential_value": random.randint(5000, 50000)
    }

#  INVENTORY OPERATIONS 
def generate_mock_inventory(n=30):
    categories = ["Electronics", "Office", "Software", "Furniture", "Supplies"]
    warehouses = ["Main", "East", "West", "North", "South"]
    data = {
        "item_id": [f"ITEM-{30000+i:05d}" for i in range(n)],
        "name": [f"Product {chr(65+i//10)}{i%10}" for i in range(n)],
        "category": random.choices(categories, k=n),
        "quantity": [random.randint(0, 100) for _ in range(n)],
        "reorder_level": [random.randint(10, 30) for _ in range(n)],
        "warehouse": random.choices(warehouses, k=n),
        "last_updated": [datetime.now().date() for _ in range(n)]
    }
    return pd.DataFrame(data)

def get_stock_levels(item_name: str = None):
    df = get_inventory()
    if item_name:
        return df[df['name'].str.contains(item_name, case=False)]
    return df

def get_low_stock_items(threshold: int = 20):
    df = get_inventory()
    df['quantity'] = pd.to_numeric(df['quantity'])
    return df[df['quantity'] < int(threshold)]

def create_inventory_item(item_id: str, name: str, category: str = "Misc", 
                          quantity: int = 0, reorder_level: int = 10, 
                          warehouse: str = "Main"):
    global _inventory_df
    df = get_inventory()
    item_id = standardize_item_id(item_id)
    
    if item_id in df['item_id'].values:
        return {"error": f"Item {item_id} already exists"}
    
    new_item = {
        "item_id": item_id,
        "name": name,
        "category": category,
        "quantity": int(quantity),
        "reorder_level": int(reorder_level),
        "warehouse": warehouse,
        "last_updated": datetime.now().date()
    }
    
    df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
    _inventory_df = df
    return new_item

def update_stock(*args, **kwargs):
    global _inventory_df
    if len(args) >= 2:
        item_id = args[0]
        quantity = args[1]
        warehouse = args[2] if len(args) >= 3 else "Main"
    else:
        item_id = kwargs.get('item_id', '')
        quantity = kwargs.get('quantity', 0)
        warehouse = kwargs.get('warehouse', "Main")
    
    df = get_inventory()
    item_id = standardize_item_id(item_id)
    warehouse = warehouse.capitalize()
    
    valid_warehouses = ["Main", "East", "West", "North", "South"]
    if warehouse not in valid_warehouses:
        return {"error": f"Invalid warehouse. Valid options: {', '.join(valid_warehouses)}"}
    
    mask = (df['item_id'] == item_id) & (df['warehouse'] == warehouse)
    
    if not mask.any():
        # Create the item if it doesn't exist
        return create_inventory_item(
            item_id=item_id,
            name=f"Item {item_id}",
            quantity=quantity,
            warehouse=warehouse
        )
    
    df.loc[mask, 'quantity'] = int(quantity)
    df.loc[mask, 'last_updated'] = datetime.now().date()
    _inventory_df = df
    return df[mask]

def generate_inventory_report(report_type: str = "valuation"):
    return {"report_type": report_type, "result": "Generated successfully"}

#  ACCOUNTS OPERATIONS 
def generate_mock_invoices(n=30):
    statuses = ["Paid", "Unpaid", "Overdue", "Partial"]
    clients = ["Global Tech", "Ocean Logistics", "Skyline Industries", "MediCorp", "EduSystems"]
    data = {
        "id": [f"INV-{50000+i:05d}" for i in range(n)],
        "client": random.choices(clients, k=n),
        "amount": [random.randint(5000, 50000) for _ in range(n)],
        "issued_date": [(datetime.now() - timedelta(days=random.randint(0, 90))).date() for _ in range(n)],
        "due_date": [(datetime.now() + timedelta(days=random.randint(1, 30))).date() for _ in range(n)],
        "status": random.choices(statuses, weights=[0.5, 0.3, 0.15, 0.05], k=n),
        "paid_amount": [0.0 for _ in range(n)]
    }
    return pd.DataFrame(data)

def create_invoice(client: str, amount: float, due_date: str = None):
    global _invoices_df
    df = get_invoices()
    
    new_id = f"INV-{50000 + len(df):05d}"
    issued = datetime.now().date()
    due = due_date or (datetime.now() + timedelta(days=30)).date()
    
    new_invoice = {
        "id": new_id,
        "client": client,
        "amount": float(amount),
        "issued_date": issued,
        "due_date": due,
        "status": "Unpaid",
        "paid_amount": 0.0
    }
    
    df = pd.concat([df, pd.DataFrame([new_invoice])], ignore_index=True)
    _invoices_df = df
    return new_invoice

def get_unpaid_invoices(client: str = None):
    df = get_invoices()
    unpaid = df[df['status'].isin(['Unpaid', 'Overdue', 'Partial'])]
    if client:
        unpaid = unpaid[unpaid['client'] == client]
    return unpaid.sort_values('due_date')

def create_payment_entry(
    invoice_id: str, 
    amount: float, 
    payment_date: str = None
) -> dict:
    """Create a payment entry for an invoice"""
    # Parse amount if it contains parameter name
    if isinstance(amount, str) and '=' in amount:
        try:
            # Extract numeric value from string
            amount = float(amount.split('=')[1].strip())
        except (ValueError, IndexError):
            return {"error": f"Invalid amount format: {amount}"}
    
    # Validate amount type
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return {"error": f"Invalid amount: {amount}. Must be a number."}
    
    # Validate invoice exists
    if not invoice_exists(invoice_id):
        return {"error": f"Invoice {invoice_id} does not exist"}
    
    # Record payment logic
    # This would connect to ERPNext API in a real implementation
    return {
        "id": invoice_id,
        "amount": 10000.0,       # Total invoice amount
        "paid_amount": 5000.0,    # Amount paid (including this payment)
        "outstanding_amount": 5000.0,  # Remaining balance
        "payment_date": payment_date or datetime.today().strftime("%Y-%m-%d")
    }

def get_revenue_snapshot(period: str = "last month"):
    return {"period": period, "revenue": random.randint(100000, 500000)}

def generate_financial_statement(statement_type: str = "P&L", period: str = "last quarter"):
    return {"statement_type": statement_type, "period": period, "amount": random.randint(50000, 200000)}

def invoice_exists(invoice_id: str) -> bool:
    """Check if an invoice exists in the system"""
    return invoice_id.startswith("INV-") and invoice_id[4:].isdigit()
#  HR OPERATIONS 
def generate_mock_employees(n=20):
    departments = ["Sales", "Marketing", "HR", "IT", "Finance", "Operations"]
    positions = ["Manager", "Specialist", "Associate", "Director", "Analyst"]
    data = {
        "id": [f"EMP-{40000+i}" for i in range(n)],
        "name": [f"Employee {i}" for i in range(n)],
        "department": random.choices(departments, k=n),
        "position": random.choices(positions, k=n),
        "hire_date": [(datetime.now() - timedelta(days=random.randint(30, 1000))).date() for _ in range(n)],
        "salary": [random.randint(30000, 120000) for _ in range(n)],
        "status": random.choices(["Active", "On Leave", "Terminated"], weights=[0.85, 0.1, 0.05], k=n)
    }
    return pd.DataFrame(data)

def get_leave_calendar(period: str = "this week"):
    today = datetime.now().date()
    if period == "this week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif period == "next week":
        start = today + timedelta(days=(7 - today.weekday()))
        end = start + timedelta(days=6)
    else:
        start = today.replace(day=1)
        end = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
    leave_data = []
    df = get_employees()
    for emp in df[df['status'] == 'Active'].sample(5).itertuples():
        leave_days = random.randint(1, 5)
        start_date = today + timedelta(days=random.randint(1, 14))
        leave_data.append({
            "employee": emp.name,
            "department": emp.department,
            "from_date": start_date,
            "to_date": start_date + timedelta(days=leave_days),
            "type": random.choice(["Vacation", "Sick", "Personal"])
        })
    return pd.DataFrame(leave_data)

def add_employee(name: str, position: str, department: str, start_date=None):
    global _employees_df
    df = get_employees()
    
    new_employee = {
        "id": f"EMP-{random.randint(40000, 49999)}",
        "name": name,
        "position": position,
        "department": department,
        "start_date": start_date or datetime.now().date().isoformat(),
        "status": "Active"
    }
    
    df = pd.concat([df, pd.DataFrame([new_employee])], ignore_index=True)
    _employees_df = df
    return new_employee

def check_contract_status(employee_name: str):
    return {
        "employee_name": employee_name,
        "contract_end_date": (datetime.now().date() + timedelta(days=random.randint(30, 365))).isoformat()
    }

def generate_hr_report(report_type: str = "headcount"):
    if report_type == "headcount":
        return {"headcount": random.randint(10, 50)}
    elif report_type == "turnover":
        return {"turnover_rate": round(random.uniform(0.05, 0.2), 2)}
    else:
        return {"report": "Unknown report type"}

def list_employees(joined_month: str = None):
    df = get_employees()
    if joined_month:
        joined_month = joined_month.strip()
        if len(joined_month) == 3:  # e.g. 'May'
            return df[df['hire_date'].apply(lambda d: d.strftime('%B')).str.lower() == joined_month.lower()]
        elif '-' in joined_month:   # e.g. '2025-05'
            return df[df['hire_date'].apply(lambda d: d.strftime('%Y-%m')) == joined_month]
        elif len(joined_month) == 4 and joined_month.isdigit(): # e.g. '2025'
            return df[df['hire_date'].apply(lambda d: d.strftime('%Y')) == joined_month]
    return df

#  MANAGEMENT OPERATIONS 
def get_sales_performance(period: str = "current quarter", top_n: int = 5):
    sales_people = [f"SP-{i}" for i in range(101, 111)]
    data = [{"name": name, "sales": random.randint(10000, 100000)} for name in sales_people]
    sorted_data = sorted(data, key=lambda x: x["sales"], reverse=True)
    return sorted_data[:top_n]

def get_business_snapshot(snapshot_type: str = "overview"):
    return {
        "revenue": random.randint(100000, 500000),
        "expenses": random.randint(50000, 200000),
        "net_profit": random.randint(20000, 100000)
    }

def get_task_summary(status: str = "pending", assignee: str = None):
    tasks = [{"task": f"Task {i}", "status": random.choice(["pending", "completed", "in progress"]), "assignee": f"EMP-{random.randint(40000, 40020)}"} for i in range(20)]
    filtered = [t for t in tasks if t["status"] == status]
    if assignee:
        filtered = [t for t in filtered if t["assignee"] == assignee]
    return filtered

def generate_strategy_report(focus_area: str = "growth"):
    return {"focus_area": focus_area, "insight": "Steady growth expected", "recommendation": "Expand sales team"}

#OPERATIONS DICTIONARY
OPERATIONS = {
    # SALES
    "get_sales_data": {
        "function": get_sales_data,
        "output_formatter": lambda data:
            "### 📊 Sales This Period\n\n"
            "| Date       | Sales (₹) |\n|:-----------|----------:|\n" +
            "\n".join([f"| {row['date']} | {row['sales']:,} |" for row in data])
            if data else "No sales data found for this period."
    },
    "get_open_orders": {
        "function": get_open_orders,
        "output_formatter": lambda data:
            "### 🗂️ Open Orders\n\n"
            "| Order ID | Customer | Product | Value (₹) | Date |\n|:---------|:---------|:--------|----------:|:-----|\n" +
            "\n".join([f"| {row['id']} | {row['customer']} | {row['product']} | {row['value']:,} | {row['date']} |" for _, row in data.iterrows()])
            if len(data) else "No open orders found."
    },
    "create_lead": {
        "function": create_lead,
        "output_formatter": lambda data:
            f"✅ **Lead Created**\n\n- **ID:** {data['id']}\n- **Company:** {data['company']}\n- **Contact:** {data['contact']}\n- **Potential Value:** ₹{data['potential_value']:,}"
    },
    # INVENTORY
    "get_stock_levels": {
        "function": get_stock_levels,
        "output_formatter": lambda data:
            "### 📦 Stock Levels\n\n" +
            ("No matching items found" if len(data) == 0 else
            "| Item | ID | Qty | Reorder @ | Warehouse |\n|:-----|:----|----:|----------:|:----------|\n" +
            "\n".join([f"| {row['name']} | {row['item_id']} | {row['quantity']} | {row['reorder_level']} | {row['warehouse']} |" for _, row in data.iterrows()]))
    },
    "get_low_stock_items": {
        "function": get_low_stock_items,
        "output_formatter": lambda data:
            "### ⚠️ Low Stock Items\n\n" +
            ("No low stock items" if len(data) == 0 else
            "\n".join([f"- **{row['name']}**: {row['quantity']} units (Reorder at {row['reorder_level']})" for _, row in data.iterrows()]))
    },
    "update_stock": {
        "function": update_stock,
        "output_formatter": lambda data: (
            f"⚠️ {data['error']}" if isinstance(data, dict) and 'error' in data else
            "✅ **Stock Updated**\n\n" +
            "\n".join([
                f"- **{row['name']}** ({row['item_id']}): {row['quantity']} units in {row['warehouse']}"
                for _, row in data.iterrows()
            ]) if hasattr(data, 'iterrows') else (
                f"✅ **New Item Created**\n\n- **ID:** {data['item_id']}\n- **Name:** {data['name']}\n- **Quantity:** {data['quantity']}"
                if isinstance(data, dict) else str(data)
            )
        )
    },
    "create_inventory_item": {
        "function": create_inventory_item,
        "output_formatter": lambda data: (
            f"⚠️ {data['error']}" if isinstance(data, dict) and 'error' in data else
            "✅ **Item Created**\n\n" +
            f"- **ID:** {data['item_id']}\n- **Name:** {data['name']}\n" +
            f"- **Category:** {data['category']}\n- **Quantity:** {data['quantity']}\n" +
            f"- **Warehouse:** {data['warehouse']}"
        )
    },
    "generate_inventory_report": {
        "function": generate_inventory_report,
        "output_formatter": lambda data:
            f"### 📃 Inventory Report\n\n- **Type:** {data.get('report_type', '-')}\n- **Result:** {data.get('result', '-')}"
    },
    # ACCOUNTS
    "get_unpaid_invoices": {
        "function": get_unpaid_invoices,
        "output_formatter": lambda data:
            "### 📝 Unpaid Invoices\n\n" +
            ("No unpaid invoices" if len(data) == 0 else
            "| Invoice | Client | Amount (₹) | Due Date |\n|:--------|:-------|-----------:|:---------|\n" +
            "\n".join([f"| {row['id']} | {row['client']} | {row['amount']:,} | {row['due_date']} |" for _, row in data.iterrows()]))
    },
    "create_payment_entry": {
        "function": create_payment_entry,
        "output_formatter": lambda data: (
            f"⚠️ {data['error']}" 
            if isinstance(data, dict) and 'error' in data 
            else (
                f"💸 **Payment Recorded**\n\n"
                f"- **Invoice:** `{data.get('id', 'N/A')}`\n"
                f"- **Amount Paid:** ₹{float(data.get('paid_amount', 0)):,.2f}\n"
                f"- **Total Paid:** ₹{float(data.get('paid_amount', 0)):,.2f}/"
                f"₹{float(data.get('amount', 0)):,.2f}\n"
                f"- **Outstanding:** ₹{float(data.get('outstanding_amount', 0)):,.2f}\n"
                f"- **Date:** {data.get('payment_date', 'N/A')}"
            )
        )
    },
    "create_invoice": {
        "function": create_invoice,
        "output_formatter": lambda data:
            f"✅ **Invoice Created**\n\n- **ID:** {data['id']}\n- **Client:** {data['client']}\n- **Amount:** ₹{data['amount']:,}\n- **Due Date:** {data['due_date']}"
    },
    "get_revenue_snapshot": {
        "function": get_revenue_snapshot,
        "output_formatter": lambda data:
            f"### 📈 Revenue for {data['period'].capitalize()}\n\n- **Total:** ₹{data['revenue']:,}"
    },
    "generate_financial_statement": {
        "function": generate_financial_statement,
        "output_formatter": lambda data:
            f"### 📊 {data['statement_type']} for {data['period']}\n\n- **Amount:** ₹{data['amount']:,}"
    },
    # HR
    "get_leave_calendar": {
        "function": get_leave_calendar,
        "output_formatter": lambda data:
            "### 📅 Leave Calendar\n\n" +
            ("No leave scheduled" if len(data) == 0 else
            "| Employee | Dept | From | To | Type |\n|:---------|:-----|:-----|:---|:-----|\n" +
            "\n".join([f"| {row['employee']} | {row['department']} | {row['from_date']} | {row['to_date']} | {row['type']} |" for _, row in data.iterrows()]))
    },
    "add_employee": {
        "function": add_employee,
        "output_formatter": lambda data:
            f"✅ **Employee Added**\n\n- **ID:** {data['id']}\n- **Name:** {data['name']}\n- **Dept:** {data['department']}\n- **Role:** {data['position']}"
    },
    "check_contract_status": {
        "function": check_contract_status,
        "output_formatter": lambda data:
            f"📝 **Contract End Date** for {data['employee_name']}:\n\n- {data['contract_end_date']}"
    },
    "generate_hr_report": {
        "function": generate_hr_report,
        "output_formatter": lambda data:
            "### 📃 HR Report\n\n" + "\n".join([f"- **{k.replace('_',' ').title()}**: {v}" for k,v in data.items()])
    },
    "list_employees": {
        "function": list_employees,
        "output_formatter": lambda data:
            "### 👥 Employees\n\n" +
            ("No employees found" if len(data) == 0 else
            "| Name | Department | Position | Hire Date |\n|:-----|:-----------|:---------|:----------|\n" +
            "\n".join([f"| {row['name']} | {row['department']} | {row['position']} | {row['hire_date']}" for _, row in data.iterrows()]))
    },
    # MANAGEMENT
    "get_sales_performance": {
        "function": get_sales_performance,
        "output_formatter": lambda data:
            "### 🏆 Sales Performance\n\n" +
            "| Name | Sales (₹) |\n|:-----|-----------:|\n" +
            "\n".join([f"| {row['name']} | {row['sales']:,} |" for row in data])
    },
    "get_business_snapshot": {
        "function": get_business_snapshot,
        "output_formatter": lambda data:
            "### 🏢 Business Snapshot\n\n" +
            f"- **Revenue:** ₹{data['revenue']:,}\n- **Expenses:** ₹{data['expenses']:,}\n- **Net Profit:** ₹{data['net_profit']:,}"
    },
    "get_task_summary": {
        "function": get_task_summary,
        "output_formatter": lambda data:
            "### 📋 Task Summary\n\n" +
            "\n".join([f"- **{t['task']}** (Status: {t['status']}, Assignee: {t['assignee']})" for t in data])
    },
    "generate_strategy_report": {
        "function": generate_strategy_report,
        "output_formatter": lambda data:
            f"### 📃 Strategy Report: {data['focus_area'].capitalize()}\n\n- **Insight:** {data['insight']}\n- **Recommendation:** {data['recommendation']}"
    },
}