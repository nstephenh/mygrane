import json
import os

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def request_to_air(endpoint: str, payload: {}):
    url = os.path.join(os.getenv("AIR_HOST"), "api/v1/", endpoint)
    return requests.post(url, data=json.dumps(payload),
                         headers={'Content-Type': 'application/json'},
                         auth=HTTPBasicAuth(os.getenv('AIR_USER'), os.getenv('AIR_PASS')))


def get_tth(filename: str):
    try:
        response_json = request_to_air("share/search", payload={
            "query":
                {"pattern": filename}
        }).json()
        print(response_json)
        return response_json[0]["tth"]
    except Exception:
        pass


if __name__ == "__main__":
    print(get_tth("2000AD 2352 (2023) (Digital-Empire).cbr"))
