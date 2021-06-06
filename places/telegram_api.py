import io
import uuid

import requests
from django.core.files.images import ImageFile

from interesting_places_bot import settings


def invoke_telegram(method, **kwargs):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    # print(f"Requesting {url} {kwargs}")
    if 'files' in kwargs:
        files = kwargs.pop('files')
        resp = requests.post(url, data=kwargs, files=files, timeout=(3.05, 27))
    else:
        resp = requests.post(url, data=kwargs, timeout=(3.05, 27))
    # print(f"Response {resp.status_code} {resp.content}")
    return resp


def get_photo(path, file_extension):
    url = f'https://api.telegram.org/file/bot{settings.TELEGRAM_BOT_TOKEN}/{path}'
    response = requests.get(url)
    name = f'{uuid.uuid4().hex}.{file_extension}'
    photo = ImageFile(io.BytesIO(response.content), name=name)
    return photo
