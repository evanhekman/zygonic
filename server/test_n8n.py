import requests
import logging
import json
import integrations
from dotenv import load_dotenv
import os

load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":
    # NOTION = os.getenv("NOTION")
    # test_params = {
    #     "action": "create",
    #     "page_name": "An Essay on Longtermism",
    #     "page_content": " \
    #         The vast majority of human beings who will ever live have not yet been born. \
    #         This simple, yet profound, observation is the foundation of longtermism, an ethical framework \
    #         that suggests our primary moral obligation is to ensure the long and flourishing future of humanity. \
    #     "
    # }

    # result1 = integrations.call_n8n_webhook(payload=test_params, webhook=NOTION)
    # print(json.dumps(result1, indent=2))

    NOTION = os.getenv("NOTION")
    test_params = {
        "action": "search",
        "query": "essay"
    }

    result2 = integrations.call_n8n_webhook(payload=test_params, webhook=NOTION)
    print(test_params)
    print(NOTION)
    print(json.dumps(result2, indent=2))

    # NOTION = os.getenv("NOTION")
    # test_params = {
    #     "action": "modify",
    #     "page_url": result1["url"],
    #     "new_content": "Extra stuff!"
    # }

    # result3 = integrations.call_n8n_webhook(payload=test_params, webhook=NOTION)
    # print(json.dumps(result3, indent=2))
