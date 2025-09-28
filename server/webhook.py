import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def webhook(integration: str, action: str, args: dict, webhook: str):
    """
    Args:
        integration: the extension to integrate with (i.e. notion)
        action: the action to perform (i.e. create_page)
        args: the information for the webhook (i.e. {page_name: ..., page_content: ...})
        webhook: the env variable for the webhook (i.e. {NOTION_N8N_WEBHOOK})
    """
    try:
        payload = {
            "integration": integration,
            "action": action,
            "args": args,
        }
        url = os.getenv(webhook)
        response = requests.post(url, json=payload, timeout=30)
        logging.info(payload)
        logging.info(response)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"webhook error: {payload}: {e}")
        return None
