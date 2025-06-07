from .base_agent import BaseAgent
from mock_erp.operations import get_sales_data, get_open_orders, create_lead
from workflows.param_wrappers import tool_with_named_args
from langchain_core.tools import Tool

class SalesAgent(BaseAgent):
    def __init__(self, use_hnsw: bool = True):
        tools = [
            Tool(
                name="GetSalesData",
                func=tool_with_named_args(get_sales_data),
                description="Retrieve sales summary for a given period (options: week, month, year)."
            ),
            Tool(
                name="GetOpenOrders",
                func=tool_with_named_args(get_open_orders),
                description="Retrieve open sales orders filtered by period (options: this month, last month, all time)."
            ),
            Tool(
                name="CreateLead",
                func=tool_with_named_args(create_lead),
                description="Create a new sales lead given company and contact."
            ),
        ]
        super().__init__("Sales", tools, use_hnsw=use_hnsw)