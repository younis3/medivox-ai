import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_available_slots():
    url = "https://cracslots.gbooking.ru/rpc"
    headers = {"Content-Type": "application/json"}

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "cracSlots.getCRACResourcesAndSlots",
        "params": {
            "start": "2025-04-10T00:00:00+00:00",
            "end": "2025-04-17T00:00:00+00:00",
            "timezone": "Europe/Moscow",
            "resources": ["PUT_RESOURCE_ID_HERE"],
            "service_ids": ["PUT_SERVICE_ID_HERE"]
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
