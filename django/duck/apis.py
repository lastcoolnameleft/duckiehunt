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
    duck_locations = DuckLocation.objects.all().values('duck_id', 'duck__name', 'latitude', 'longitude', 'comments')
    summary = list(duck_locations)
    return JsonResponse(summary, safe=False, content_type='application/json')

def duck_locations(request, duck_id):
    duck_locations = DuckLocation.objects.filter(duck_id=duck_id).values('duck_id', 'duck__name', 'latitude', 'longitude', 'comments')
    summary = list(duck_locations)
    return JsonResponse(summary, safe=False, content_type='application/json')

def duck_photos(request, duck_id):
    photos = DuckLocationPhoto.objects.filter(duck_location__duck_id=duck_id)
    summary = list(photos)
    return JsonResponse(summary, safe=False, content_type='application/json')

def location(request, duck_location_id):
    duck_location = get_object_or_404(DuckLocation, pk=duck_location_id)
    duck_location_data = {
        'duck_id': duck_location.duck_id,
        'latitude': duck_location.latitude,
        'longitude': duck_location.longitude,
        'date_time': duck_location.date_time,
        'comments': duck_location.comments,
    }
    return JsonResponse(duck_location_data)

