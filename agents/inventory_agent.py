from .base_agent import BaseAgent
from mock_erp.operations import (
    get_stock_levels,
    get_low_stock_items,
    update_stock,
    generate_inventory_report,
    create_inventory_item
)
from workflows.param_wrappers import tool_with_named_args
from langchain_core.tools import Tool

class InventoryAgent(BaseAgent):
    def __init__(self, use_hnsw: bool = True):
        tools = [
            Tool(
                name="GetStockLevels",
                func=tool_with_named_args(get_stock_levels),
                description="Get stock levels for a specific item or all items."
            ),
            Tool(
                name="GetLowStockItems",
                func=tool_with_named_args(get_low_stock_items),
                description="Identify items below a reorder threshold."
            ),
            Tool(
                name="UpdateStock",
                func=tool_with_named_args(update_stock),
                description=(
                    "Update stock quantity. "
                    "Parameters: item_id (required), quantity (required), warehouse (optional). "
                    "Example: 'item_id=ITEM-30001, quantity=50, warehouse=Main'"
                )
            ),
            Tool(
                name="CreateInventoryItem",
                func=tool_with_named_args(create_inventory_item),
                description=(
                    "Create a new inventory item. "
                    "Parameters: item_id (required), name (required), category (optional), "
                    "quantity (optional, default 0), reorder_level (optional, default 10), "
                    "warehouse (optional, default 'Main'). "
                    "Example: 'item_id=ITEM-30001, name=Product XYZ, category=Electronics, quantity=50'"
                )
            ),
            Tool(
                name="GenerateInventoryReport",
                func=tool_with_named_args(generate_inventory_report),
                description="Generate inventory valuation or movement report."
            )
        ]
        super().__init__("Inventory", tools, use_hnsw=use_hnsw)