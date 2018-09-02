from django.contrib import admin

# Register your models here.
from .models import Duck, DuckLocation, DuckLocationLink, DuckLocationPhoto

admin.site.register(Duck)
admin.site.register(DuckLocation)
admin.site.register(DuckLocationLink)
admin.site.register(DuckLocationPhoto)

