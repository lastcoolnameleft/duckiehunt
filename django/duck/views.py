""" Views for Django """
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.cache import cache
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from duck import marker

from .forms import CreateDuckForm, DuckForm, LoginForm, RegistrationForm
from .models import Duck, DuckLocation, DuckLocationLink, DuckLocationPhoto

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 300


def _get_login_attempts_key(request):
    """Get cache key for login rate limiting based on IP."""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
    return f'login_attempts_{ip}'


def _is_login_rate_limited(request):
    """Check if the IP has exceeded login attempts."""
    key = _get_login_attempts_key(request)
    attempts = cache.get(key, 0)
    return attempts >= LOGIN_RATE_LIMIT


def _record_failed_login(request):
    """Record a failed login attempt."""
    key = _get_login_attempts_key(request)
    attempts = cache.get(key, 0)
    cache.set(key, attempts + 1, LOGIN_RATE_WINDOW)


def _clear_login_attempts(request):
    """Clear login attempts on successful login."""
    key = _get_login_attempts_key(request)
    cache.delete(key)


def index(request):
    """ / path """
    map_data = {
        'width': '100%',
        'height': '550px',
        'focus_lat': 23,
        'focus_long': 10,
        'focus_zoom': 2,
        'location_list_api': '/api/locations',
        'duck_location_id': 0,
    }
    total_distance = Duck.objects.aggregate(total_distance=Sum('total_distance'))['total_distance'] or 0
    recent_locations = DuckLocation.objects.select_related('duck').order_by('-date_time')[:5]

    return render(request, 'duck/main.html', {
        'map': map_data,
        'total_ducks': Duck.objects.count(),
        'total_locations': DuckLocation.objects.count(),
        'total_distance': total_distance,
        'recent_locations': recent_locations,
    })

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
    duck_links = list(
        DuckLocationLink.objects.filter(duck_location_id=duck_location_id)
        .exclude(link__isnull=True)
        .exclude(link='')
        .values_list('link', flat=True)
    )

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
                   'duck_links': duck_links, 'duck_list': duck_dropdown_list})

def duck_list(request):
    """ lists all ducks """
    ducks = Duck.objects.order_by('-total_distance', 'duck_id')
    return render(request, 'duck/list.html', {
        'duck_list': ducks,
        'duck_count': ducks.count(),
    })

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

def _get_next_url(request, default='/mark/'):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default


def mark(request, duck_id=None):
    user = request.user if request.user.is_authenticated else None
    form_page = f'/mark/{duck_id}' if duck_id else '/mark/'
    require_captcha = not request.user.is_authenticated
    # Skip captcha when no real reCAPTCHA keys are configured (dev/test)
    if getattr(settings, 'RECAPTCHA_PUBLIC_KEY', '') == getattr(settings, 'TEST_RECAPTCHA_PUBLIC_KEY', ''):
        require_captcha = False
    return mark_process(
        request,
        duck_id,
        user,
        form_page,
        require_captcha=require_captcha,
    )


def mark_captcha(request, duck_id=None):
    return redirect('mark', duck_id=duck_id) if duck_id else redirect('mark')

def mark_process(request, duck_id, user, form_page, require_captcha=True):
    """ Adds a duck, location, photo and link from webform """
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = DuckForm(request.POST, request.FILES, require_captcha=require_captcha)
        # check whether it's valid:
        if form.is_valid():
            duck_id = form.cleaned_data['duck_id']

            # Duck #2 is special — only user_id=1 can check it in
            if duck_id == 2 and (not user or user.id != 1):
                form.add_error('duck_id', 'Duck #2 is reserved.')
                return render(request, 'duck/mark.html', {'form': form, 'map': {
                    'width': '100%', 'height': '400px', 'location_list': [], 'duck_location_id': 0,
                }, 'form_page': form_page})

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

            image = form.cleaned_data.get('image')
            if image:
                try:
                    photo_info = marker.handle_uploaded_file(image, duck_id,
                                                            duck.name, form.cleaned_data['comments'])
                    duck_location_photo = DuckLocationPhoto(duck_location=duck_location,
                                                            flickr_photo_id=photo_info['id'],
                                                            flickr_thumbnail_url=photo_info['sizes']['Small 320']['source'])
                    duck_location_photo.save()
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.exception('Photo upload failed for duck #%s', duck_id)
                    # Sighting is still saved — photo just won't be attached

            duck.total_distance = round(DuckLocation.objects.filter(duck_id=duck_id).aggregate(Sum('distance_to'))['distance_to__sum'], 2)
            duck.save()

            # redirect to a new URL:
            new_location_url = '/location/' + str(duck_location.duck_location_id)

            # Only send email notification for approved submissions
            if duck_location.approved == 'Y':
                marker.email_duck_location(duck_id, new_location_url)

            return HttpResponseRedirect(new_location_url)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = DuckForm(initial={'duck_id': duck_id}, require_captcha=require_captcha)

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


@login_required
def create_duck(request):
    """Register a new duck."""
    from .forms import CreateDuckForm
    from .utils import next_available_duck_id, is_valid_duck_number
    from django.utils import timezone

    suggested_id = next_available_duck_id()

    if request.method == 'POST':
        form = CreateDuckForm(request.POST)
        if form.is_valid():
            duck_id = form.cleaned_data['duck_id']
            name = form.cleaned_data['name']

            # Auto-assign if not provided
            if duck_id is None:
                duck_id = next_available_duck_id()

            duck = Duck(
                duck_id=duck_id,
                name=name,
                create_time=timezone.now(),
                created_by=request.user,
                comments='',
            )
            duck.save()
            return redirect('detail', duck_id=duck.duck_id)
    else:
        form = CreateDuckForm()

    return render(request, 'duck/create.html', {
        'form': form,
        'suggested_id': suggested_id,
    })


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')


def login(request):
    """Display and process username/password login."""
    next_url = request.GET.get('next')
    if request.user.is_authenticated:
        return redirect(_get_next_url(request))

    error = None
    if _is_login_rate_limited(request):
        error = 'Too many login attempts. Please try again in a few minutes.'
        form = LoginForm()
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                _clear_login_attempts(request)
                auth_login(request, user)
                return redirect(_get_next_url(request))
            _record_failed_login(request)
            error = 'Invalid username or password.'
    else:
        form = LoginForm()

    return render(request, 'duck/login.html', {'form': form, 'next': next_url, 'error': error})


def register(request):
    """Display and process registration."""
    next_url = request.GET.get('next')
    if request.user.is_authenticated:
        return redirect(_get_next_url(request))

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
            )
            if user is not None:
                auth_login(request, user)
            return redirect(_get_next_url(request))
    else:
        form = RegistrationForm()

    return render(request, 'duck/register.html', {'form': form, 'next': next_url})


@login_required(login_url='/login')
def profile(request):
    """Show profile data with user's duck location history."""
    user = request.user
    locations = DuckLocation.objects.filter(user=user).select_related('duck').order_by('-date_time')
    return render(request, 'duck/profile.html', {
        'user': user,
        'locations': locations,
        'location_count': locations.count(),
    })

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)
