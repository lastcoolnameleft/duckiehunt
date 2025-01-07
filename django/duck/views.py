""" Views for Django """
from operator import ne
from django.core import serializers
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings
from .models import Duck, DuckLocation, DuckLocationPhoto
from .forms import DuckForm
from duck import marker 

def index(request):
    """ / path """
    map_data = {
        'width': '100%',
        'height': '800px',
        'focus_lat': 23,
        'focus_long': 10,
        'focus_zoom': 2,
        'location_list_api': '/api/locations',
        'duck_location_id': 0,
    }

    return render(request, 'duck/main.html', {'map': map_data})

def found(request, duck_id):
    """ /found/# path """
    try:
        duck = Duck.objects.get(pk=duck_id)
    except Duck.DoesNotExist:
        duck = None

    return render(request, 'duck/found.html', {'duck_id': duck_id, 'duck': duck})

def detail(request, duck_id):
    """ /duck/# path """
    try:
        duck = Duck.objects.get(pk=duck_id)
    except Duck.DoesNotExist:
        return render(request, 'duck/detail-not-found.html', {'duck_id': duck_id})

    photos = DuckLocationPhoto.objects.filter(duck_location__duck_id=duck_id)

    # SCREW YOU DJANGO FOR NOT SUPPORT USING SELECT_RELATED + SERIALIZATION
    # https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
    # https://stackoverflow.com/questions/34666892/trying-to-serialize-a-queryset-that-uses-select-related-cant-obtain-fields-o
    # https://docs.djangoproject.com/en/2.1/topics/serialization/#serialization-of-natural-keys
    duck_location_list = DuckLocation.objects.filter(duck_id=duck_id)
    map_data = {
        'width': '100%',
        'height': '400px',
        'focus_lat': 0,
        'focus_long': 0,
        'focus_zoom': 2,
        'location_list_api': '/api/duck/' + str(duck_id) + '/locations',
        'duck_location_id': 0,
    }
    duck_dropdown_list = Duck.objects.all()

    return render(request, 'duck/detail.html',
                  {'duck': duck, 'photos': photos, 'map': map_data,
                   'duck_location_list': duck_location_list, 'duck_list': duck_dropdown_list})

def location(request, duck_location_id):
    """ Show /duck/$duck_id """
    duck_location = get_object_or_404(DuckLocation, pk=duck_location_id)

    photos = DuckLocationPhoto.objects.filter(duck_location_id=duck_location_id)

    duck_location_list = DuckLocation.objects.filter(duck_id=duck_location.duck.duck_id)
    duck_location_json = serializers.serialize('json', duck_location_list, use_natural_foreign_keys=True)
    map_data = {
        'width': '100%',
        'height': '400px',
        'focus_lat': 0,
        'focus_long': 0,
        'focus_zoom': 15,
        'location_list_api': '/api/location/' + str(duck_location_id),
        'duck_location_id': duck_location_id,
    }
    duck_dropdown_list = Duck.objects.all()

    return render(request, 'duck/location.html',
                  {'photos': photos, 'map': map_data, 'duck': duck_location.duck,
                   'duck_location': duck_location, 'duck_location_list': duck_location_list,
                   'duck_list': duck_dropdown_list})

def duck_list(request):
    """ lists all ducks """
    ducks = Duck.objects.all()
    return render(request, 'duck/list.html', {'duck_list': ducks})

def faq(request):
    """ shows faq """
    return render(request, 'duck/faq.html')

def issue(request):
    """ shows issue """
    return render(request, 'duck/issue.html')

def tos(request):
    """ shows terms of service """
    return render(request, 'duck/tos.html')

def privacy(request):
    """ shows privacy """
    return render(request, 'duck/privacy.html')

@login_required
def mark(request, duck_id=None):
    user = request.user
    url = '/mark/' + str(duck_id) if duck_id else '/mark/'
    return mark_process(request, duck_id, user, url)

def mark_captcha(request, duck_id=None):
    user = None
    return mark_process(request, duck_id, user, '/mark_captcha/')

def mark_process(request, duck_id, user, form_page):
    """ Adds a duck, location, photo and link from webform """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DuckForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            duck_id = form.cleaned_data['duck_id']
            try:
                duck = Duck.objects.get(pk=duck_id)
                if duck.name == 'Unnamed' and form.cleaned_data['name'] != 'Unnamed':
                    duck.name = form.cleaned_data['name']
            except Duck.DoesNotExist:
                name = form.cleaned_data['name'] if form.cleaned_data['name'] else 'Unnamed'
                duck = marker.create_new_duck(duck_id, name)

            duck_location = marker.add_duck_location(duck_id,
                                                     form.cleaned_data['lat'],
                                                     form.cleaned_data['lng'],
                                                     form.cleaned_data['location'],
                                                     form.cleaned_data['date_time'],
                                                     form.cleaned_data['comments'],
                                                     user)

            if request.FILES and request.FILES['image']:
                #marker.add_duck_location_photo(duck_location, request.FILES['image'], duck_id, duck.name, form.cleaned_data['comments'])
                photo_info = marker.handle_uploaded_file(request.FILES['image'], duck_id,
                                                        duck.name, form.cleaned_data['comments'])
                duck_location_photo = DuckLocationPhoto(duck_location=duck_location,
                                                        flickr_photo_id=photo_info['id'],
                                                        flickr_thumbnail_url=photo_info['sizes']['Small 320']['source'])
                duck_location_photo.save()

            duck.total_distance = round(DuckLocation.objects.filter(duck_id=duck_id).aggregate(Sum('distance_to'))['distance_to__sum'], 2)
            duck.save()

            # redirect to a new URL:
            new_location_url = '/location/' + str(duck_location.duck_location_id)

            marker.email_duck_location(duck_id, new_location_url)

            return HttpResponseRedirect(new_location_url)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = DuckForm(initial={'duck_id': duck_id})

    map_data = {
        'width': '100%',
        'height': '400px',
        'focus_lat': 35,
        'focus_long': -30,
        'focus_zoom': 1,
        'location_list': [],
        'duck_location_id': 0,
    }
    return render(request, 'duck/mark.html', {'form': form, 'map': map_data, 'form_page': form_page})

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')

def login(request):
    """Home view, displays login mechanism"""
    next = request.GET.get('next', None)
    if next and len(next.split('/')) > 2:
        duck_id = next.split('/')[2]
    else:
        duck_id = None
    return render(request, 'duck/login.html', {'next': next, 'duck_id': duck_id})

def profile(request):
    """ Show profile data """
    print(request.user.username)
    return render(request, 'duck/profile.html', {'user': request.user})