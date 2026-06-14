""" Views for Django """
import logging
import os
import secrets
from pathlib import Path
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from django.core.cache import cache
from django.db.models import Count, Sum, Subquery, OuterRef
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from django_q.tasks import async_task

from duck import marker

from .forms import CreateDuckForm, DuckForm, LoginForm, RegistrationForm
from .linkedin_tokens import (
    build_linkedin_authorize_url,
    linkedin_exchange_code_for_token,
    linkedin_fetch_person_urn,
    linkedin_refresh_access_token,
    upsert_env_values,
)
from .models import Duck, DuckLocation, DuckLocationLink, DuckLocationPhoto

LOGIN_RATE_LIMIT = 5
LOGIN_RATE_WINDOW = 300
logger = logging.getLogger(__name__)
LINKEDIN_STATE_SESSION_KEY = 'linkedin_oauth_state'


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

def found(request, duck_id=None):
    """ /found path (generic) and /found/# path (specific duck) """
    duck = None
    if duck_id is not None:
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

def leaderboard(request):
    """ /leaderboard path """
    # Top 10 most traveled ducks
    top_traveled = (
        Duck.objects.annotate(location_count=Count('ducklocation'))
        .filter(total_distance__gt=0)
        .order_by('-total_distance')[:10]
    )

    # Top 10 most spotted ducks (by number of sightings)
    most_spotted = (
        Duck.objects.annotate(location_count=Count('ducklocation'))
        .filter(location_count__gt=1)
        .order_by('-location_count')[:10]
    )

    # Top 10 spotters (users with most sightings)
    top_spotters = (
        DuckLocation.objects.filter(user__isnull=False)
        .values('user__username')
        .annotate(
            sighting_count=Count('duck_location_id'),
            unique_ducks=Count('duck_id', distinct=True),
        )
        .order_by('-sighting_count')[:10]
    )

    # 10 most recently active ducks
    recently_active = (
        DuckLocation.objects.select_related('duck')
        .filter(approved='Y')
        .order_by('-date_time')[:10]
    )

    # Top 10 longest single jumps
    longest_jumps_qs = (
        DuckLocation.objects.filter(distance_to__gt=0, approved='Y')
        .select_related('duck')
        .order_by('-distance_to')[:10]
    )
    # Annotate with previous location name
    longest_jumps = []
    for loc in longest_jumps_qs:
        prev = (
            DuckLocation.objects
            .filter(duck_id=loc.duck_id, date_time__lt=loc.date_time)
            .order_by('-date_time')
            .values_list('location', flat=True)
            .first()
        )
        loc.prev_location = prev
        longest_jumps.append(loc)

    return render(request, 'duck/leaderboard.html', {
        'top_traveled': top_traveled,
        'most_spotted': most_spotted,
        'top_spotters': top_spotters,
        'recently_active': recently_active,
        'longest_jumps': longest_jumps,
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

            images = form.cleaned_data.get('image') or []
            if not isinstance(images, (list, tuple)):
                images = [images]

            for image in images:
                # Save each image to disk for upload to provider.
                image_path = marker.save_uploaded_file(image, settings.UPLOAD_PATH)
                # Create a local-first photo record so every image is immediately visible.
                photo = DuckLocationPhoto.objects.create(
                    duck_location=duck_location,
                    local_path=os.path.basename(image_path),
                )
                # Queue async upload to provider (Flickr, Imgur, etc.).
                photo_task_id = async_task(
                    'duck.tasks.upload_photo',
                    photo.duck_location_photo_id,
                    image_path,
                    duck_id,
                    duck.name,
                    form.cleaned_data['comments'],
                )
                logger.info(
                    "Queued photo upload task %s for duck #%s (location=%s, photo=%s, local_path=%s)",
                    photo_task_id,
                    duck_id,
                    duck_location.duck_location_id,
                    photo.duck_location_photo_id,
                    photo.local_path,
                )

            duck.total_distance = round(DuckLocation.objects.filter(duck_id=duck_id).aggregate(Sum('distance_to'))['distance_to__sum'], 2)
            duck.save()

            # redirect to a new URL:
            new_location_url = '/location/' + str(duck_location.duck_location_id)

            # Queue email and social sharing in background
            if duck_location.approved == 'Y':
                email_task_id = async_task('duck.tasks.send_email_notification', duck_id, new_location_url)
                social_task_id = async_task('duck.tasks.share_to_social', duck_location.duck_location_id)
                logger.info(
                    "Queued notification tasks for duck #%s (location=%s, email_task=%s, social_task=%s)",
                    duck_id,
                    duck_location.duck_location_id,
                    email_task_id,
                    social_task_id,
                )

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


def _resolve_active_env_file():
    project_root = Path(getattr(settings, 'PROJECT_ROOT', '.'))
    env_file = os.environ.get('ENV_FILE', '').strip()
    if env_file:
        env_path = Path(env_file)
        if not env_path.is_absolute():
            env_path = project_root / env_path
        return env_path
    return project_root / '.env'


def _linkedin_scopes():
    return os.environ.get('LI_SCOPES', 'w_member_social openid profile')


def _linkedin_redirect_uri(request):
    configured_uri = getattr(settings, 'LI_REDIRECT_URI', '').strip()
    if configured_uri:
        return configured_uri
    return request.build_absolute_uri(reverse('admin_linkedin_callback'))


def _set_runtime_values(updates):
    for key, value in updates.items():
        os.environ[key] = value
        setattr(settings, key, value)


def _persist_linkedin_tokens(request, token_data):
    updates = {
        'LI_ACCESS_TOKEN': token_data['access_token'],
        'LI_REDIRECT_URI': _linkedin_redirect_uri(request),
    }
    refresh_token = token_data.get('refresh_token')
    if refresh_token:
        updates['LI_REFRESH_TOKEN'] = refresh_token
    expires_in = token_data.get('expires_in')
    if expires_in is not None:
        updates['LI_ACCESS_TOKEN_EXPIRES_IN'] = str(expires_in)

    person_urn = linkedin_fetch_person_urn(
        updates['LI_ACCESS_TOKEN'],
        getattr(settings, 'LI_API_VERSION', ''),
    )
    if person_urn:
        updates['LI_PERSON_URN'] = person_urn

    env_path = _resolve_active_env_file()
    upsert_env_values(env_path, updates)
    _set_runtime_values(updates)
    return env_path


@staff_member_required(login_url='/admin/login/')
def linkedin_token_admin(request):
    return render(request, 'duck/linkedin_token_admin.html', {
        'linkedin_configured': bool(getattr(settings, 'LI_ACCESS_TOKEN', '')),
        'has_refresh_token': bool(getattr(settings, 'LI_REFRESH_TOKEN', '')),
        'active_env_file': str(_resolve_active_env_file()),
        'callback_uri': _linkedin_redirect_uri(request),
    })


@staff_member_required(login_url='/admin/login/')
def linkedin_token_refresh(request):
    if request.method != 'POST':
        return redirect('admin_linkedin_token')

    client_id = getattr(settings, 'LI_CLIENT_ID', '')
    client_secret = getattr(settings, 'LI_CLIENT_SECRET', '')
    if not client_id or not client_secret:
        messages.error(request, 'Missing LI_CLIENT_ID or LI_CLIENT_SECRET.')
        return redirect('admin_linkedin_token')

    refresh_token = getattr(settings, 'LI_REFRESH_TOKEN', '')
    if refresh_token:
        try:
            token_data = linkedin_refresh_access_token(refresh_token, client_id, client_secret)
            env_path = _persist_linkedin_tokens(request, token_data)
            messages.success(request, f'LinkedIn token refreshed. Updated {env_path}.')
        except Exception:
            logger.exception('LinkedIn refresh token flow failed')
            messages.error(request, 'Refresh token flow failed. Starting OAuth consent flow instead.')
        else:
            return redirect('admin_linkedin_token')

    state = secrets.token_urlsafe(24)
    request.session[LINKEDIN_STATE_SESSION_KEY] = state
    authorize_url = build_linkedin_authorize_url(
        client_id,
        _linkedin_redirect_uri(request),
        _linkedin_scopes(),
        state,
    )
    return redirect(authorize_url)


@staff_member_required(login_url='/admin/login/')
def linkedin_token_callback(request):
    expected_state = request.session.get(LINKEDIN_STATE_SESSION_KEY, '')
    incoming_state = request.GET.get('state', '')
    if not expected_state or expected_state != incoming_state:
        messages.error(request, 'LinkedIn OAuth state mismatch. Please try refresh again.')
        return redirect('admin_linkedin_token')

    request.session.pop(LINKEDIN_STATE_SESSION_KEY, None)
    code = request.GET.get('code', '')
    if not code:
        messages.error(request, 'LinkedIn callback missing authorization code.')
        return redirect('admin_linkedin_token')

    client_id = getattr(settings, 'LI_CLIENT_ID', '')
    client_secret = getattr(settings, 'LI_CLIENT_SECRET', '')
    try:
        token_data = linkedin_exchange_code_for_token(
            code,
            client_id,
            client_secret,
            _linkedin_redirect_uri(request),
        )
        env_path = _persist_linkedin_tokens(request, token_data)
    except Exception:
        logger.exception('LinkedIn OAuth callback token exchange failed')
        messages.error(request, 'LinkedIn token exchange failed.')
        return redirect('admin_linkedin_token')

    messages.success(request, f'LinkedIn token updated successfully. Updated {env_path}.')
    return redirect('admin_linkedin_token')

def custom_403(request, exception):
    import sentry_sdk
    sentry_sdk.capture_message(f"403: {request.path}", level="warning")
    return render(request, '403.html', status=403)


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    import sentry_sdk
    sentry_sdk.capture_exception()
    return render(request, '500.html', status=500)
