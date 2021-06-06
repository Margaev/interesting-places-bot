import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.gis.geos import Point
from django.db.models import Q

from places.telegram_api import invoke_telegram, get_photo
from places.utils import send_places, make_place_message
from places import models


@csrf_exempt
def telegram_hook(request):
    update = json.loads(request.body)
    # print(json.dumps(update, indent=4))

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']

        tg_user, created = models.TgUser.objects.get_or_create(
            tg_id=user_id
        )

        # update user info
        tg_user.first_name = update['message']['from'].get('first_name')
        tg_user.last_name = update['message']['from'].get('last_name')
        tg_user.username = update['message']['from'].get('username')

        if created:
            tg_user.expecting_input = False

        tg_user.save()

        if 'text' in update['message']:
            update_text = update['message']['text']

            if tg_user.expecting_input:
                new_place = models.Place.objects.filter(
                    Q(author=tg_user) & (Q(name=None) | Q(description=None) | Q(photo__exact=''))
                ).first()

                if new_place:
                    if new_place.name is None:
                        new_place.name = update_text.split('\n')[0]
                        text = 'Введите описание'
                        invoke_telegram('sendMessage', chat_id=chat_id, text=text)
                    elif new_place.description is None:
                        new_place.description = update_text
                        if not new_place.photo:
                            text = 'Пришлите фото'
                            invoke_telegram('sendMessage', chat_id=chat_id, text=text)
                        else:
                            text = 'Место успешно добавлено'
                            invoke_telegram('sendMessage', chat_id=chat_id, text=text)

                            tg_user.expecting_input = False
                            tg_user.save()

                    new_place.save()
                else:
                    print('No Place object found')

            elif '/start' in update_text:
                text = 'Привет! Этот бот показывает интересные места по близости к тебе в Санкт-Петербурге.\n' \
                       'Чтобы получить места поблизости, пошли свою геопозицию.'
                find_places_button = {
                    'text': 'Найти места поблизости!',
                    'request_location': True
                }
                add_place_button = {
                    'text': 'Добавить новое место'
                }
                keyboard = {
                    'keyboard': [[find_places_button, ], [add_place_button, ]],
                    'resize_keyboard': True
                }
                invoke_telegram('sendMessage', chat_id=chat_id, text=text, reply_markup=json.dumps(keyboard))

            elif 'Добавить новое место' in update_text:
                tg_user.expecting_input = True
                tg_user.save()

                text = 'Пришлите геопозицию'
                invoke_telegram('sendMessage', chat_id=chat_id, text=text)

        elif 'location' in update['message']:
            x = update['message']['location']['longitude']
            y = update['message']['location']['latitude']

            if tg_user.expecting_input:
                existing_place = models.Place.objects.filter(
                    Q(author=tg_user) & (Q(name=None) | Q(description=None) | Q(photo__exact=''))
                ).first()

                if existing_place is not None:
                    text = 'Вы уже начали добавление нового места'
                    invoke_telegram('sendMessage', chat_id=chat_id, text=text)
                else:
                    models.Place.objects.create(
                        author=tg_user,
                        location=Point(x, y, srid=4326),
                        name=None,
                        description=None,
                        photo=None,
                    )

                    text = 'Введите название'
                    invoke_telegram('sendMessage', chat_id=chat_id, text=text)
            else:
                send_places(chat_id, user_id, x, y)

        elif 'photo' in update['message']:
            if tg_user.expecting_input:
                photo_id = update['message']['photo'][-1]['file_id']
                file_path = invoke_telegram('getFile', file_id=photo_id).json()['result']['file_path']
                file_extension = file_path.split('.')[-1]
                photo = get_photo(file_path, file_extension)

                existing_place = models.Place.objects.filter(
                    Q(author=tg_user) & (Q(name=None) | Q(description=None) | Q(photo__exact=''))
                ).first()

                if existing_place is not None:
                    existing_place.photo = photo
                    existing_place.save()

                    if existing_place.name is not None and existing_place.description is not None:
                        text = 'Место успешно добавлено'
                        invoke_telegram('sendMessage', chat_id=chat_id, text=text)

                        tg_user.expecting_input = False
                        tg_user.save()
                else:
                    print('No Place object found')

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
