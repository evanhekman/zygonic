import requests
import logging
import json
import integrations
from dotenv import load_dotenv
import os

load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Define your webhook URL and the arguments.
    address = os.getenv("LOCAL_ADDR")
    url = f"{address}/task"
    params = {"task": "Write essay on longtermism"}

    response = requests.get(url, params=params)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))
