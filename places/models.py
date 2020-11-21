from django.db import models
from django.contrib.gis.db import models as gis_models

from interesting_places_bot import settings


class Place(models.Model):
    location = gis_models.PointField(spatial_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=511, null=True, blank=True)
    photo = models.ImageField(upload_to='./', null=True, blank=True)

    def get_photo_url(self):
        return f'https://{settings.URL}{self.photo.url}'

    def __str__(self):
        return self.name
