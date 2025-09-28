import requests
import logging
import json
import server.integrations as integrations
from dotenv import load_dotenv
import os

load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Define your webhook URL and the arguments.
    N8N_NOTION_CREATE_PAGE = os.getenv("N8N_NOTION_CREATE_PAGE")
    test_params = {
        "page_name": "An Essay on Longtermism",
        "page_content": " \
            The vast majority of human beings who will ever live have not yet been born. \
            This simple, yet profound, observation is the foundation of longtermism, an ethical framework \
            that suggests our primary moral obligation is to ensure the long and flourishing future of humanity. \
        "
    }

    result = integrations.call_n8n_webhook(payload=test_params, webhook=N8N_NOTION_CREATE_PAGE)
    print(json.dumps(result, indent=2))
