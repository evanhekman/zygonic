import os
import requests
import logging
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Webhook Configuration ---
# All Notion-related actions go to the same webhook.
# The 'action' field in the payload tells n8n how to route it.
NOTION = os.getenv("NOTION")


# ==============================================================================
# 2. TOOL IMPLEMENTATIONS (PYTHON FUNCTIONS)
# ==============================================================================

def call_n8n_webhook(payload: dict, webhook: str):
    """Generic function to send a formatted payload to an n8n webhook."""
    try:
        response = requests.post(webhook, json=payload, timeout=30)
        logging.info(response)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling webhook {webhook}: {e}")
        return None

# --- Specific Notion Functions ---

def create_notion_page(page_name: str, page_content: str):
    """Implementation for creating a Notion page."""
    return call_n8n_webhook(
        payload={"action": "create", "page_name": page_name, "page_content": page_content},
        webhook=NOTION,
    )

def search_notion_page(query: str):
    """Implementation for searching a Notion page."""
    return call_n8n_webhook(
        payload={"action": "search", "query": query},
        webhook=NOTION
    )

def modify_notion_page(page_url: str, new_content: str):
    """Implementation for modifying a Notion page."""
    return call_n8n_webhook(
        payload={"action": "modify", "page_url": page_url, "new_content": new_content},
        webhook=NOTION
    )

# --- Action Dictionary: Maps tool names from the spec to the Python functions ---
ACTIONS = {
    "notion.create_page": create_notion_page,
    "notion.search_page": search_notion_page,
    "notion.modify_page": modify_notion_page,
}


# ==============================================================================
# 3. TOOL EXECUTOR
#    (This function links the agent's output to your code)
# ==============================================================================

def execute_tool(tool_name: str, parameters: dict):
    """
    Finds and executes the appropriate Python function based on the tool name.

    Args:
        tool_name (str): The name of the tool to execute (e.g., 'notion.create_page').
        parameters (dict): The parameters for the function, as provided by the LLM.

    Returns:
        The result of the executed function.
    """
    if tool_name not in ACTIONS:
        return f"Error: Tool '{tool_name}' is not a valid action."

    function_to_call = ACTIONS[tool_name]
    
    try:
        logging.info(f"Executing tool '{tool_name}' with params: {parameters}")
        # Use dictionary unpacking to pass parameters to the function
        result = function_to_call(**parameters)
        return result
    except TypeError as e:
        logging.error(f"Type error executing {tool_name}: {e}. Check if parameters match function signature.")
        return f"Error: Invalid parameters for tool '{tool_name}'. Details: {e}"
    except Exception as e:
        logging.error(f"An unexpected error occurred while executing {tool_name}: {e}")
        return f"Error: An unexpected error occurred while running '{tool_name}'."
