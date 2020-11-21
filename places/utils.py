import json


from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

from places import models
from places.telegram_api import invoke_telegram


def get_nearest_places(x, y):
    point = Point(x, y, srid=4326)
    res = models.Place.objects.annotate(distance=Distance('location', point)).order_by('distance')[:5]
    return res


def make_place_message(suggestions_index, tg_user, chat_id, delete_message_id=None):
    place = models.Place.objects.get(id=tg_user.current_suggestions[suggestions_index]['place_id'])

    text = f'{place.name}\n\nОписание:\n{place.description}'
    photo_url = place.get_photo_url()
    text += f'\n\nМесто расположено в {round(tg_user.current_suggestions[suggestions_index]["distance"], 2)} км от вас'

    previous_suggestion_index = suggestions_index - 1 if suggestions_index != 0 else len(tg_user.current_suggestions) - 1
    button_previous = {
        'text': '<-',
        'callback_data': str({'action': 'previous_place',
                              'suggestion_index': previous_suggestion_index})
    }

    next_suggestion_index = suggestions_index + 1 if suggestions_index != len(tg_user.current_suggestions) - 1 else 0
    button_next = {
        'text': '->',
        'callback_data': str({'action': 'next_place',
                              'suggestion_index': next_suggestion_index})
    }

    send_location_button = {
        'text': 'Показать местоположение',
        'callback_data': str({'action': 'send_location',
                              'place_id': place.id})
    }

    keyboard = {
        'inline_keyboard': [[button_previous, button_next], [send_location_button, ]]
    }

    # invoke_telegram('sendPhoto', chat_id=chat_id, photo=photo_url, caption=text, reply_markup=json.dumps(keyboard))
    #
    # if delete_message_id is not None:
    #     invoke_telegram('deleteMessage', chat_id=chat_id, message_id=delete_message_id)

    if delete_message_id is None:
        invoke_telegram('sendPhoto', chat_id=chat_id, photo=photo_url, caption=text, reply_markup=json.dumps(keyboard))
    else:
        invoke_telegram(
            'editMessageMedia',
            chat_id=chat_id,
            message_id=delete_message_id,
            media=json.dumps({'type': 'photo', 'media': photo_url})
        )

        invoke_telegram(
            'editMessageCaption',
            chat_id=chat_id,
            message_id=delete_message_id,
            caption=text,
            reply_markup=json.dumps(keyboard)
        )


def send_places(chat_id, user_id, x, y):
    print('sending')
    tg_user, _ = models.TgUser.objects.get_or_create(tg_id=user_id)
    tg_user.current_suggestions = [{'place_id': place.id, 'distance': place.distance.km}
                                   for place in get_nearest_places(x, y)]
    tg_user.save()

    make_place_message(0, tg_user, chat_id)
