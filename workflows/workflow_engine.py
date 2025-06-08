from workflows.self_correction import correct_parameters
from mock_erp.operations import OPERATIONS
from workflows.self_correction import SelfCorrectionSystem

def execute_workflow(operation_name: str, params: dict) -> str:
    """
    Execute an ERP operation workflow, with parameter validation and correction.

    Args:
        operation_name (str): The name of the operation to execute.
        params (dict): The parameters for the operation.

    Returns:
        str: The formatted result of the operation, or an error message if the operation fails.
    """
    try:
        # Get operation function from OPERATIONS
        operation = OPERATIONS.get(operation_name)
        if not operation:
            return f"⚠️ Operation '{operation_name}' not found"
        
        # Validate and correct parameters
        corrected_params = correct_parameters(operation["function"], params)
        
        # Execute operation with corrected parameters
        result = operation["function"](**corrected_params)
        
        # Format and return output
        return operation["output_formatter"](result)
    
    except Exception as e:
        # Attempt self-correction of parameters
        correction = SelfCorrectionSystem.correct(operation_name, params, str(e))
        if correction:
            return execute_workflow(operation_name, correction)
        return f"❌ Operation failed: {str(e)}"
