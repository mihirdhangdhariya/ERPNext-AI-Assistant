from .base_agent import BaseAgent
from mock_erp.operations import (
    get_unpaid_invoices,
    create_payment_entry,
    get_revenue_snapshot,
    generate_financial_statement,
    create_invoice
)
from workflows.param_wrappers import tool_with_named_args
from langchain_core.tools import Tool

class AccountsAgent(BaseAgent):
    def __init__(self, use_hnsw: bool = True):
        tools = [
            Tool(
                name="GetUnpaidInvoices",
                func=tool_with_named_args(get_unpaid_invoices),
                description="Retrieve unpaid invoices optionally filtered by client."
            ),
            Tool(
                name="create_payment_entry",
                func=tool_with_named_args(create_payment_entry),
                description=(
                    "Record a payment against an invoice. "
                    "Parameters: invoice_id (required), amount (required), payment_date (optional). "
                    "Example: 'invoice_id=\"INV-50001\", amount=5000'"
                )
            ),
            Tool(
                name="GetRevenueSnapshot",
                func=tool_with_named_args(get_revenue_snapshot),
                description="Get revenue summary for a given period (e.g. 'last month', 'this quarter')."
            ),
            Tool(
                name="GenerateFinancialStatement",
                func=tool_with_named_args(generate_financial_statement),
                description="Generate financial statements. Parameters: statement_type (e.g. 'P&L', 'Balance Sheet'), period (e.g. 'last quarter')."
            ),
            Tool(
                name="CreateInvoice",
                func=tool_with_named_args(create_invoice),
                description=(
                    "Create a new invoice. "
                    "Parameters: client (required), amount (required), due_date (optional). "
                    "Example: 'client=Global Tech, amount=10000'"
                )
            ),
        ]
        super().__init__("Accounts", tools, use_hnsw=use_hnsw)