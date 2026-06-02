# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Duck(models.Model):
    duck_id = models.IntegerField(primary_key=True)
    create_time = models.DateTimeField(blank=True)
    name = models.CharField(max_length=128, blank=True, default=None)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_ducks')
    comments = models.TextField(blank=True, default=None)
    total_distance = models.FloatField(blank=True, default=0)
    approved = models.CharField(max_length=1, default='Y')

    def natural_key(self):
        return {'duck_id': self.duck_id, 'name': self.name, 'total_distance': self.total_distance}

    class Meta:
        db_table = 'duck'


class DuckLocation(models.Model):
    duck_location_id = models.AutoField(primary_key=True)
    duck = models.ForeignKey(Duck, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    link = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    duck_history_id = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True, db_index=True)
    location = models.TextField(blank=True, null=True)
    approved = models.CharField(max_length=1, blank=True, null=True)
    distance_to = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'duck_location'


class DuckLocationLink(models.Model):
    duck_location_link_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, on_delete=models.CASCADE, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'duck_location_link'


class DuckLocationPhoto(models.Model):
    duck_location_photo_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, on_delete=models.CASCADE, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    flickr_thumbnail_url = models.TextField(blank=True, null=True)
    # Provider-agnostic fields (for migration away from Flickr)
    photo_provider = models.CharField(max_length=50, blank=True, null=True)
    photo_id = models.CharField(max_length=255, blank=True, null=True)
    thumbnail_url = models.TextField(blank=True, null=True)
    # Local file path relative to UPLOAD_PATH (for backup/local serving)
    local_path = models.CharField(max_length=512, blank=True, null=True)

    @property
    def display_thumbnail_url(self):
        """Return the best available photo URL.

        Priority: provider thumbnail > legacy Flickr URL > local file.
        """
        if self.thumbnail_url:
            return self.thumbnail_url
        if self.flickr_thumbnail_url:
            return self.flickr_thumbnail_url
        if self.local_path:
            return f'/media/{self.local_path}'
        return ''

    class Meta:
        db_table = 'duck_location_photo'
