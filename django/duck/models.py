# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Duck(models.Model):
    duck_id = models.IntegerField(primary_key=True)
    create_time = models.DateTimeField(blank=True)
    name = models.CharField(max_length=128, blank=True, default=None)
    #current_owner_id = models.IntegerField(blank=True, null=True)
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
    link = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    duck_history_id = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    approved = models.CharField(max_length=1, blank=True, null=True)
    distance_to = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'duck_location'


class DuckLocationLink(models.Model):
    duck_location_link_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, models.DO_NOTHING, null=True)
    link = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'duck_location_link'


class DuckLocationPhoto(models.Model):
    duck_location_photo_id = models.AutoField(primary_key=True)
    duck_location = models.ForeignKey(DuckLocation, models.DO_NOTHING, null=True)
    flickr_photo_id = models.BigIntegerField(blank=True, null=True)
    flickr_thumbnail_url = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'duck_location_photo'

