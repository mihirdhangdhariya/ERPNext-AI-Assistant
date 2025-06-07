from .base_agent import BaseAgent
from mock_erp.operations import (
    get_sales_performance,
    get_business_snapshot,
    get_task_summary,
    generate_strategy_report
)
from workflows.param_wrappers import tool_with_named_args
from langchain_core.tools import Tool

class ManagementAgent(BaseAgent):
    def __init__(self, use_hnsw: bool = True):
        tools = [
            Tool(
                name="GetSalesPerformance",
                func=tool_with_named_args(get_sales_performance),
                description="Retrieve top performing salespeople or teams."
            ),
            Tool(
                name="GetBusinessSnapshot",
                func=tool_with_named_args(get_business_snapshot),
                description="Get a business health overview including revenue and expenses."
            ),
            Tool(
                name="GetTaskSummary",
                func=tool_with_named_args(get_task_summary),
                description="Provide a summary of tasks with optional filters."
            ),
            Tool(
                name="GenerateStrategyReport",
                func=tool_with_named_args(generate_strategy_report),
                description="Generate strategic reports with insights."
            ),
        ]
        super().__init__("Management", tools, use_hnsw=use_hnsw)