from django.contrib import admin
from places import models
from leaflet.admin import LeafletGeoAdmin


@admin.register(models.Place)
class PointAdmin(LeafletGeoAdmin):
    pass


admin.site.register(models.TgUser)
