from .base_agent import BaseAgent
from mock_erp.operations import (
    get_leave_calendar,
    add_employee,
    check_contract_status,
    generate_hr_report,
    list_employees
)
from workflows.param_wrappers import tool_with_named_args
from langchain_core.tools import Tool

class HRAgent(BaseAgent):
    def __init__(self, use_hnsw: bool = True):
        tools = [
            Tool(
                name="GetLeaveCalendar",
                func=tool_with_named_args(get_leave_calendar),
                description="Show who's on leave in a specific period."
            ),
            Tool(
                name="AddEmployee",
                func=tool_with_named_args(add_employee),
                description="Add a new employee to the system."
            ),
            Tool(
                name="CheckContractStatus",
                func=tool_with_named_args(check_contract_status),
                description="Check the contract end date for an employee."
            ),
            Tool(
                name="GenerateHRReport",
                func=tool_with_named_args(generate_hr_report),
                description="Generate HR reports such as headcount and turnover."
            ),
            Tool(
                name="ListEmployees",
                func=tool_with_named_args(list_employees),
                description="List employees, optionally filtering by joined_month (e.g. 'May', '2025-05', or '2025')."
            ),
        ]
        super().__init__("HR", tools, use_hnsw=use_hnsw)