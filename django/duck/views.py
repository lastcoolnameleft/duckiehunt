from django.core import serializers
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime
from .models import Duck, DuckLocation, DuckLocationPhoto
from .forms import DuckForm

def index(request):
    duck_location_list = DuckLocation.objects.all()
    duck_location_json = serializers.serialize('json', duck_location_list, use_natural_foreign_keys=True)
    map_data = {
        'width': '100%',
        'height': '800px',
        'focus_lat': 23,
        'focus_long': 10,
        'focus_zoom': 2,
        'location_list': duck_location_json,
        'duck_location_id': 0,
    }

    return render(request, 'duck/main.html', {'map': map_data})

def detail(request, duck_id):
    duck = get_object_or_404(Duck, pk=duck_id)
    photos = DuckLocationPhoto.objects.filter(duck_location__duck_id=duck_id)

    # SCREW YOU DJANGO FOR NOT SUPPORT USING SELECT_RELATED + SERIALIZATION
    # https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
    # https://stackoverflow.com/questions/34666892/trying-to-serialize-a-queryset-that-uses-select-related-cant-obtain-fields-o
    # https://docs.djangoproject.com/en/2.1/topics/serialization/#serialization-of-natural-keys
    duck_location_list = DuckLocation.objects.filter(duck_id=duck_id)
    duck_location_json = serializers.serialize('json', duck_location_list, use_natural_foreign_keys=True)
    map_data = {
        'width': '100%',
        'height': '400px',
        'focus_lat': 0,
        'focus_long': 0,
        'focus_zoom': 2,
        'location_list': duck_location_json,
        'duck_location_id': 0,
    }
    duck_dropdown_list = Duck.objects.all()

    return render(request, 'duck/detail.html',
                  {'duck': duck, 'photos': photos, 'map': map_data,
                   'duck_location_list': duck_location_list, 'duck_list': duck_dropdown_list})

def location(request, duck_location_id):
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
        'location_list': duck_location_json,
        'duck_location_id': duck_location_id,
    }
    duck_dropdown_list = Duck.objects.all()

    return render(request, 'duck/location.html',
                  {'photos': photos, 'map': map_data, 'duck': duck_location.duck,
                   'duck_location': duck_location, 'duck_location_list': duck_location_list, 'duck_list': duck_dropdown_list})

def duck_list(request):
    ducks = Duck.objects.all()
    return render(request, 'duck/list.html', {'duck_list': ducks})

def faq(request):
    return render(request, 'duck/faq.html')

def mark(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DuckForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            duck_id = form.cleaned_data['duck_id']
            try:
                duck = Duck.objects.get(pk=duck_id)
            except Duck.DoesNotExist:
                name = form.cleaned_data['name'] if form.cleaned_data['name'] else 'Unnamed'
                duck = Duck(duck_id=duck_id,
                            name=name, approved='Y',
                            create_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            comments='')
                duck.save()
            #user = Users(id=1)
            duck_location = DuckLocation(duck=duck,
                                         latitude=form.cleaned_data['lat'],
                                         longitude=form.cleaned_data['lng'],
                                         location=form.cleaned_data['location'],
                                         date_time=form.cleaned_data['date_time'],
                                         comments=form.cleaned_data['comments'],
                                         #user=user,
                                         approved='Y')
            duck_location.save()

            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/duck/' + str(duck_id))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = DuckForm()
        map_data = {
            'width': '100%',
            'height': '400px',
            'focus_lat': 35,
            'focus_long': -30,
            'focus_zoom': 1,
            'location_list': [],
            'duck_location_id': 0,
        }

    return render(request, 'duck/mark.html', {'form': form, 'map': map_data})
