from geopy.distance import distance

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from places import models
from places.telegram_api import invoke_telegram


def get_nearest_places(x, y):
    point = Point(x, y, srid=4326)
    res = models.Place.objects.annotate(distance=Distance('location', point)).order_by('distance')[:5]
    return res


def send_places(chat_id, x, y):
    places = get_nearest_places(x, y)

    text = f'Ближайшие места:'
    invoke_telegram('sendMessage', chat_id=chat_id, text=text)

    for place in places:
        text = f'{place.name}\n\nОписание:\n{place.description}'
        photo_url = place.get_photo_url()

        text += f'\n\nМесто расположено в {round(place.distance.km, 2)} км от вас'

        invoke_telegram('sendPhoto', chat_id=chat_id, photo=photo_url, caption=text)
        invoke_telegram('sendLocation', chat_id=chat_id, longitude=place.location.x, latitude=place.location.y)
