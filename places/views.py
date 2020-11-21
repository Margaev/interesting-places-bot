from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json

from places.telegram_api import invoke_telegram
from places.utils import send_places, make_place_message
from places import models


@csrf_exempt
def telegram_hook(request):
    update = json.loads(request.body)
    # print(json.dumps(update, indent=4))
    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']

        if 'text' in update['message']:
            update_text = update['message']['text']
            if '/start' in update_text:
                models.TgUser.objects.get_or_create(tg_id=user_id)

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
            send_places(chat_id, user_id, x, y)
    elif 'callback_query' in update:
        chat_id = update['callback_query']['message']['chat']['id']
        user_id = update['callback_query']['from']['id']
        message_id = update['callback_query']['message']['message_id']
        data = json.loads(update['callback_query']['data'].replace("'", '"'))
        tg_user, _ = models.TgUser.objects.get_or_create(tg_id=user_id)

        if data['action'] == 'send_location':
            place = models.Place.objects.get(id=data['place_id'])

            invoke_telegram(
                'sendLocation',
                chat_id=chat_id,
                longitude=place.location.x,
                latitude=place.location.y
            )
        elif data['action'] == 'next_place':
            make_place_message(
                suggestions_index=data['suggestion_index'],
                tg_user=tg_user,
                chat_id=chat_id,
                delete_message_id=message_id
            )
        elif data['action'] == 'previous_place':
            make_place_message(
                suggestions_index=data['suggestion_index'],
                tg_user=tg_user,
                chat_id=chat_id,
                delete_message_id=message_id
            )

    return HttpResponse('ok')
