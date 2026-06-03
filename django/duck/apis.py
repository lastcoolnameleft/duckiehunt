import os
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import Duck, DuckLocation, DuckLocationPhoto
from django.db.models import F

def duck_detail(request, duck_id):
    duck = get_object_or_404(Duck, pk=duck_id)
    duck_data = {
        'duck_id': duck.duck_id,
        'name': duck.name,
        'total_distance': duck.total_distance,
        'create_time': duck.create_time,
        'approved': duck.approved
    }
    return JsonResponse(duck_data)

def ducks_all(request):
    duck_locations = Duck.objects.all().values('duck_id', 'name', 'total_distance')
    summary = list(duck_locations)
    return JsonResponse(summary, safe=False, content_type='application/json')

def locations_all(request):
    duck_locations = list(
        DuckLocation.objects.all()
        .order_by('duck_id', 'date_time', 'duck_location_id')
        .values(
            'duck_location_id',
            'duck_id',
            'duck__name',
            'latitude',
            'longitude',
            'location',
            'date_time',
            'comments',
        )
    )
    _attach_location_photos(duck_locations)
    summary = duck_locations
    return JsonResponse(summary, safe=False, content_type='application/json')

def duck_locations(request, duck_id):
    duck_locations = list(
        DuckLocation.objects.filter(duck_id=duck_id)
        .order_by('date_time', 'duck_location_id')
        .values(
            'duck_location_id',
            'duck_id',
            'duck__name',
            'latitude',
            'longitude',
            'location',
            'date_time',
            'comments',
        )
    )
    _attach_location_photos(duck_locations)
    summary = duck_locations
    return JsonResponse(summary, safe=False, content_type='application/json')

def location(request, duck_location_id):
    duck_location = get_object_or_404(DuckLocation, pk=duck_location_id)
    duck_location_data = {
        'duck_location_id': duck_location.duck_location_id,
        'duck_id': duck_location.duck_id,
        'latitude': duck_location.latitude,
        'longitude': duck_location.longitude,
        'location': duck_location.location,
        'date_time': duck_location.date_time,
        'comments': duck_location.comments,
    }
    _attach_location_photo(duck_location_data, duck_location.duck_location_id)
    return JsonResponse(duck_location_data)


def _attach_location_photos(duck_locations):
    if not duck_locations:
        return

    location_ids = [location['duck_location_id'] for location in duck_locations]
    photos_by_location = {}
    for photo in (
        DuckLocationPhoto.objects.filter(duck_location_id__in=location_ids)
        .order_by('duck_location_id', 'duck_location_photo_id')
    ):
        photos_by_location.setdefault(photo.duck_location_id, photo.display_thumbnail_url)

    for location in duck_locations:
        location['photo_thumbnail_url'] = photos_by_location.get(location['duck_location_id'], '')


def _attach_location_photo(duck_location_data, duck_location_id):
    photo = (
        DuckLocationPhoto.objects.filter(duck_location_id=duck_location_id)
        .order_by('duck_location_photo_id')
        .first()
    )
    duck_location_data['photo_thumbnail_url'] = photo.display_thumbnail_url if photo else ''

def health(request):
    from django.db import connection

    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status = 'ok' if db_ok else 'degraded'
    code = 200 if db_ok else 503
    return JsonResponse(
        {'status': status, 'sha': os.environ.get('GIT_SHA', 'unknown'), 'db': db_ok},
        status=code,
    )


def version(request):
    return JsonResponse({
        'git_sha': os.environ.get('GIT_SHA', 'unknown'),
    })
