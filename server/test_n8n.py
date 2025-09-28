import requests
import logging
import json
import integrations
import webhook
from action import Action
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":

    if len(sys.argv) > 1:
        print(f"Script name: {sys.argv[0]}")
        print("Arguments provided:")
        for i, arg in enumerate(sys.argv[1:]):
            print(f"  Argument {i+1}: {arg}")
        arg = sys.argv[1]
    else:
        print("No arguments provided.")
        exit(1)

    if arg == "notion":
        url = "NOTION"
        test_create = Action(integration=arg, 
                        action="create",
                        args={
                            "page_name": "An Essay on Longtermism",
                            "page_content": "The vast majority of human beings who will ever live have not yet been born. \n\
                            This simple, yet profound, observation is the foundation of longtermism, an ethical framework \
                            that suggests our primary moral obligation is to ensure the long and flourishing future of humanity. "
                        },
                        webhook=url)
        result1 = test_create.call()
        print(json.dumps(result1, indent=2))

        test_search = Action(integration=arg, 
                        action="search",
                        args={
                            "query": "essay"
                        },
                        webhook=url)
        print(json.dumps(test_search.call(), indent=2))

        test_modify = Action(integration=arg, 
                        action="modify",
                        args={
                            "page_url": result1["url"],
                            "new_content": "Extra stuff!"
                        },
                        webhook=url)
        print(json.dumps(test_modify.call(), indent=2))
    
    elif arg == "email":
        webhook = os.getenv("EMAIL")
        test_params = {
            "action": "create",
            "page_name": "An Essay on Longtermism",
            "page_content": " \
                ougugughgh my epic emaillllllllllllll business!!! \
            "
        }
        result1 = integrations.call_n8n_webhook(payload=test_params, webhook=webhook)
        print(json.dumps(result1, indent=2))

        url = "EMAIL"
        test_create = Action(integration=arg, 
                        action="create",
                        args={
                            "page_name": "An Essay on Longtermism",
                            "page_content": "The vast majority of human beings who will ever live have not yet been born. \n\
                            This simple, yet profound, observation is the foundation of longtermism, an ethical framework \
                            that suggests our primary moral obligation is to ensure the long and flourishing future of humanity. "
                        },
                        webhook=url)
        result1 = test_create.call()
        print(json.dumps(result1, indent=2))

