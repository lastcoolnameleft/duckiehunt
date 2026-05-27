"""Form definitions for Duckiehunt."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django_recaptcha.fields import ReCaptchaField


User = get_user_model()


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
    duck_id = forms.IntegerField(label='Duck #', min_value=2, max_value=3000, widget=forms.NumberInput(attrs={'style': 'width: 6em;'}))
    name = forms.CharField(label='Duck name', max_length=100, disabled=False, required=False)
    location = forms.CharField(label='Location', max_length=100)
    date_time = forms.DateTimeField(
        label='Date/Time',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%m/%d/%Y %H:%M:%S'],
    )
    lat = forms.FloatField(label='Latitude', widget=forms.HiddenInput())
    lng = forms.FloatField(label='Longitude', widget=forms.HiddenInput())
    comments = forms.CharField(widget=forms.Textarea(attrs={'cols': '50', 'rows': '5'}))
    image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        require_captcha = kwargs.pop('require_captcha', True)
        super().__init__(*args, **kwargs)
        if not require_captcha:
            del self.fields['captcha']

        for field_name, field in self.fields.items():
            if field_name != 'captcha' and not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['class'] = 'form-control'
