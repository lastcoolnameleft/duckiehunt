"""Form definitions for Duckiehunt."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django_recaptcha.fields import ReCaptchaField


User = get_user_model()
MAX_PHOTOS_PER_SIGHTING = 5
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return [] if not self.required else super().clean(data, initial)

        files = data if isinstance(data, (list, tuple)) else [data]
        if len(files) > MAX_PHOTOS_PER_SIGHTING:
            raise forms.ValidationError(
                f'You can upload at most {MAX_PHOTOS_PER_SIGHTING} photos per sighting.'
            )

        cleaned_files = []
        for uploaded_file in files:
            cleaned_file = super().clean(uploaded_file, initial)
            if cleaned_file and cleaned_file.size > MAX_IMAGE_SIZE_BYTES:
                raise forms.ValidationError('Image file is too large (max 10MB). Please resize and try again.')
            cleaned_files.append(cleaned_file)
        return cleaned_files


class RegistrationForm(UserCreationForm):
    """Registration form with captcha protection."""

    email = forms.EmailField(required=False)
    captcha = ReCaptchaField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('username', 'email', 'password1', 'password2'):
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Username/password login form."""

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )


class DuckForm(forms.Form):
    """Form for duck sightings."""

    captcha = ReCaptchaField()
    duck_id = forms.IntegerField(label='Duck #', min_value=2, max_value=99999, widget=forms.NumberInput(attrs={'style': 'width: 6em;'}))
    name = forms.CharField(label='Duck name', max_length=100, disabled=False, required=False)
    location = forms.CharField(label='Location', max_length=100)
    date_time = forms.DateTimeField(
        label='Date/Time',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%m/%d/%Y %H:%M:%S'],
    )
    lat = forms.FloatField(label='Latitude', widget=forms.HiddenInput())
    lng = forms.FloatField(label='Longitude', widget=forms.HiddenInput())
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': '50', 'rows': '5'}))
    image = MultipleImageField(required=False)

    def __init__(self, *args, **kwargs):
        require_captcha = kwargs.pop('require_captcha', True)
        super().__init__(*args, **kwargs)
        if not require_captcha:
            del self.fields['captcha']

        for field_name, field in self.fields.items():
            if field_name != 'captcha' and not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = 'form-control'


COMMUNITY_DUCK_MIN_ID = 5000


class CreateDuckForm(forms.Form):
    """Form for registering a new duck."""

    duck_id = forms.IntegerField(
        label='Duck #',
        required=False,
        min_value=COMMUNITY_DUCK_MIN_ID,
        max_value=99999,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank for auto-assign'}),
        help_text=f'Must be {COMMUNITY_DUCK_MIN_ID} or higher and not a prime number. Leave blank to get the next available number.',
    )
    name = forms.CharField(
        label='Duck name',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Give your duck a name'}),
    )

    def clean_duck_id(self):
        from .utils import is_valid_duck_number
        from .models import Duck

        duck_id = self.cleaned_data.get('duck_id')
        if duck_id is None:
            return duck_id

        if not is_valid_duck_number(duck_id):
            raise forms.ValidationError('Duck numbers cannot be prime numbers.')

        if Duck.objects.filter(duck_id=duck_id).exists():
            raise forms.ValidationError(f'Duck #{duck_id} is already taken.')

        return duck_id
