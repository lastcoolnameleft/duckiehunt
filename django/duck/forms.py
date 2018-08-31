from django import forms
import datetime

class DuckForm(forms.Form):
    duck_id = forms.IntegerField(label='Duck #')
    name = forms.CharField(label='Duck name', max_length=100, disabled=True, required=False)
    location = forms.CharField(label='Location', max_length=100)
    date_time = forms.DateTimeField(label='Date/Time', 
                                initial=datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    lat = forms.FloatField(label='Latitude')
    lng = forms.FloatField(label='Longitude')
