from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.core import serializers
from .models import Duck, DuckLocation, DuckLocationPhoto

def detail(request, duck_id):
    duck = get_object_or_404(Duck, pk=duck_id)
    duck_json = serializers.serialize('json', [duck,])
    return HttpResponse(duck_json, content_type='application/json')
