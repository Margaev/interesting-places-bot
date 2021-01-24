from django.db import models
from django.contrib.gis.db import models as gis_models

from interesting_places_bot import settings


class TgUser(models.Model):
    tg_id = models.CharField(max_length=63)
    current_suggestions = models.JSONField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    first_name = models.CharField(max_length=63, null=True, blank=True)
    last_name = models.CharField(max_length=63, null=True, blank=True)
    username = models.CharField(max_length=63, null=True, blank=True)


class Place(models.Model):
    location = gis_models.PointField(spatial_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=511, null=True, blank=True)
    photo = models.ImageField(upload_to='./', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def get_photo_url(self):
        return f'https://{settings.URL}{self.photo.url}'

    def __str__(self):
        return self.name
