""" Form for Duckiehunt """
from django import forms
import datetime

class DuckForm(forms.Form):
    """ Form for duckiehunt.  """
    duck_id = forms.IntegerField(label='Duck #', min_value=2, max_value=3000)
    name = forms.CharField(label='Duck name', max_length=100, disabled=False, required=False)
    location = forms.CharField(label='Location', max_length=100)
    date_time = forms.DateTimeField(label='Date/Time',
                                    initial=datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    lat = forms.FloatField(label='Latitude')
    lng = forms.FloatField(label='Longitude')
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': '50', 'rows': '5'}))
    image = forms.ImageField(required=False)
