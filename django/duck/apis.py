import os
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from .models import Duck, DuckLocation
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



def share_sighting(request, duck_location_id):
    """Share a duck sighting to configured social media platforms.

    POST /api/share/<duck_location_id>/
    Optional query param: ?platform=facebook (to share to a specific platform)
    """
    from django.contrib.auth.decorators import login_required
    from django.views.decorators.http import require_POST

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    from .models import DuckLocationPhoto
    from .social import share_to, share_to_all, SocialShareError

    duck_location = get_object_or_404(DuckLocation, pk=duck_location_id)

    # Get the photo URL if available
    photo = DuckLocationPhoto.objects.filter(duck_location=duck_location).first()
    photo_url = None
    if photo:
        photo_url = photo.display_thumbnail_url

    platform = request.GET.get('platform')
    try:
        if platform:
            results = {platform: share_to(platform, duck_location, photo_url)}
        else:
            results = share_to_all(duck_location, photo_url)
    except SocialShareError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'results': results})
