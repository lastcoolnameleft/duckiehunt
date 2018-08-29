from django.core import serializers
from django.shortcuts import get_object_or_404, render
from .models import Duck, DuckLocation, DuckLocationPhoto

def index(request):
    duck_location_list = DuckLocation.objects.all().select_related()
    duck_location_json = (serializers.serialize('json', duck_location_list,
                                                use_natural_foreign_keys=True,
                                                use_natural_primary_keys=True))
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

    # SCREW YOU DJANGO AND YOUR CRAPPY ASS ORM THAT DOES NOT SUPPORT USING SELECT_RELATED + SERIALIZATION
    # https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
    # https://stackoverflow.com/questions/34666892/trying-to-serialize-a-queryset-that-uses-select-related-cant-obtain-fields-o
    # I JUST LOST 2 HOURS, FURTHER FUELING MY ANGER AND HATRED FOR ORM's
    # https://docs.djangoproject.com/en/2.1/topics/serialization/#serialization-of-natural-keys
    duck_location_list = DuckLocation.objects.filter(duck_id=duck_id).select_related()
    duck_location_json = (serializers.serialize('json', duck_location_list,
                                                use_natural_foreign_keys=True,
                                                use_natural_primary_keys=True))
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
    return render(request, 'duck/location.html', {'duck_location': duck_location})

def duck_list(request):
    ducks = Duck.objects.all()
    return render(request, 'duck/list.html', {'duck_list': ducks})

def faq(request):
    return render(request, 'duck/faq.html')
