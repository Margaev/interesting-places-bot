from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

from places.telegram_api import invoke_telegram
from places.utils import send_places
from places import models


@csrf_exempt
def telegram_hook(request):
    update = json.loads(request.body)
    chat_id = update['message']['chat']['id']
    # print(json.dumps(update, indent=4))

    if 'text' in update['message']:
        update_text = update['message']['text']
        if '/start' in update_text:
            text = 'Привет! Этот бот показывает интересные места по близости к тебе в Санкт-Петербурге.\n' \
                   'Чтобы получить места поблизости, пошли свою геопозицию.'
            button = {
                'text': 'Найти места поблизости!',
                'request_location': True
            }
            keyboard = {
                'keyboard': [[button, ], ],
                'resize_keyboard': True
            }
            invoke_telegram('sendMessage', chat_id=chat_id, text=text, reply_markup=json.dumps(keyboard))

    elif 'location' in update['message']:
        x = update['message']['location']['longitude']
        y = update['message']['location']['latitude']
        send_places(chat_id=chat_id, x=x, y=y)

    return HttpResponse('ok')
