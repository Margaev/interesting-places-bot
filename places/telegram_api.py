import requests
from interesting_places_bot import settings


def invoke_telegram(method, **kwargs):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    # print(f"Requesting {url} {kwargs}")
    resp = requests.post(url, data=kwargs, timeout=(3.05, 27))
    # print(f"Response {resp.status_code} {resp.content}")
    return resp
