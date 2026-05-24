"""Tests for duck views (page rendering, auth, redirects)"""
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from duck.models import Duck, DuckLocation, DuckLocationPhoto


TEST_RECAPTCHA_SETTINGS = {
    'RECAPTCHA_PUBLIC_KEY': '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    'RECAPTCHA_PRIVATE_KEY': '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    'SILENCED_SYSTEM_CHECKS': ['django_recaptcha.recaptcha_test_key_error'],
}


def captcha_success_response():
    return SimpleNamespace(is_valid=True, error_codes=[], extra_data={}, action=None)


class HomepageViewTest(TestCase):
    def test_homepage_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'duck/main.html')

    def test_homepage_has_map_context(self):
        response = self.client.get('/')
        self.assertIn('map', response.context)
        self.assertEqual(response.context['map']['location_list_api'], '/api/locations')


class FoundViewTest(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(
            duck_id=1, name='Found Duck', create_time=timezone.now(), comments=''
        )

    def test_found_existing_duck(self):
        response = self.client.get('/found/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/found.html')

    def test_found_nonexistent_duck(self):
        """found view handles missing duck gracefully (no 404)"""
        response = self.client.get('/found/999')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/found.html')

    def test_found_context_contains_duck_for_existing(self):
        response = self.client.get('/found/1')
        self.assertEqual(response.context['duck'], self.duck)

    def test_found_context_duck_is_none_for_missing(self):
        response = self.client.get('/found/999')
        self.assertIsNone(response.context['duck'])


class DuckDetailViewTest(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(
            duck_id=1, name='Detail Duck', create_time=timezone.now(), comments=''
        )

    def test_existing_duck(self):
        response = self.client.get('/duck/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/detail.html')

    def test_nonexistent_duck_shows_not_found_template(self):
        response = self.client.get('/duck/999')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/detail-not-found.html')

    def test_view_duck_alternate_url(self):
        response = self.client.get('/view/duck/1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/detail.html')

    def test_detail_context_contains_duck_and_map(self):
        response = self.client.get('/duck/1')
        self.assertEqual(response.context['duck'], self.duck)
        self.assertIn('map', response.context)
        self.assertEqual(response.context['map']['location_list_api'], '/api/duck/1/locations')


class LocationViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'test@test.com', 'pass')
        self.duck = Duck.objects.create(
            duck_id=1, name='Loc Duck', create_time=timezone.now(), comments=''
        )
        self.location = DuckLocation.objects.create(
            duck=self.duck, user=self.user,
            latitude=32.0, longitude=-96.0,
            location='Test City', date_time=timezone.now(),
            comments='Test', distance_to=0, approved='Y',
        )

    def test_existing_location(self):
        response = self.client.get(f'/location/{self.location.duck_location_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/location.html')

    def test_nonexistent_location_returns_404(self):
        response = self.client.get('/location/99999')
        self.assertEqual(response.status_code, 404)

    def test_view_location_alternate_url(self):
        response = self.client.get(f'/view/location/{self.location.duck_location_id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/location.html')

    def test_location_context_contains_duck_and_map(self):
        response = self.client.get(f'/location/{self.location.duck_location_id}')
        self.assertEqual(response.context['duck'], self.duck)
        self.assertEqual(response.context['duck_location'], self.location)
        self.assertIn('map', response.context)


class DuckListViewTest(TestCase):
    def test_duck_list_returns_200(self):
        response = self.client.get('/duck/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/list.html')

    def test_duck_list_contains_ducks(self):
        Duck.objects.create(duck_id=1, name='Duck A', create_time=timezone.now(), comments='')
        Duck.objects.create(duck_id=2, name='Duck B', create_time=timezone.now(), comments='')
        response = self.client.get('/duck/')
        self.assertContains(response, 'Duck A')
        self.assertContains(response, 'Duck B')

    def test_duck_list_empty(self):
        response = self.client.get('/duck/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['duck_list']), [])


class StaticPagesViewTest(TestCase):
    def test_faq(self):
        response = self.client.get('/faq/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/faq.html')

    def test_tos(self):
        response = self.client.get('/tos/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/tos.html')

    def test_privacy(self):
        response = self.client.get('/privacy/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/privacy.html')

    def test_issue(self):
        response = self.client.get('/issue/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/issue.html')


class AuthViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('tester', 'test@test.com', 'pass')

    def test_mark_shows_captcha_for_anonymous_users(self):
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/mark.html')
        self.assertContains(response, 'recaptcha')

    def test_mark_accessible_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/mark.html')

    def test_mark_with_duck_id_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/mark/5')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form_page'], '/mark/5')

    def test_mark_captcha_redirects_to_mark(self):
        response = self.client.get('/mark_captcha/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/mark/')

    def test_mark_captcha_redirects_to_mark_with_duck_id(self):
        response = self.client.get('/mark_captcha/42')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/mark/42')

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/login.html')
        self.assertIn('form', response.context)

    def test_login_page_keeps_next_param(self):
        response = self.client.get('/login?next=/mark/42')
        self.assertEqual(response.context['next'], '/mark/42')

    def test_login_page_no_next(self):
        response = self.client.get('/login')
        self.assertIsNone(response.context['next'])

    def test_login_post_with_valid_credentials_logs_in(self):
        response = self.client.post('/login?next=/mark/5', {'username': 'tester', 'password': 'pass'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/mark/5')
        self.assertEqual(self.client.session.get('_auth_user_id'), str(self.user.pk))

    def test_login_post_with_invalid_credentials_shows_error(self):
        response = self.client.post('/login', {'username': 'tester', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/login.html')
        self.assertContains(response, 'Invalid username or password.')

    def test_logout_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_profile_requires_login(self):
        self.client.force_login(self.user)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/profile.html')


@override_settings(**TEST_RECAPTCHA_SETTINGS)
class RegistrationViewTest(TestCase):
    def _valid_data(self, **overrides):
        data = {
            'username': 'newtester',
            'email': 'new@test.com',
            'password1': 'DuckStrongPass123!',
            'password2': 'DuckStrongPass123!',
            'g-recaptcha-response': 'PASSED',
        }
        data.update(overrides)
        return data

    def test_register_get_shows_form(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/register.html')
        self.assertIn('form', response.context)

    @patch('django_recaptcha.fields.client.submit')
    def test_register_post_creates_user_and_logs_in(self, mock_submit):
        mock_submit.return_value = captcha_success_response()
        response = self.client.post('/register/?next=/mark/7', self._valid_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/mark/7')
        user = User.objects.get(username='newtester')
        self.assertEqual(user.email, 'new@test.com')
        self.assertEqual(self.client.session.get('_auth_user_id'), str(user.pk))

    @patch('django_recaptcha.fields.client.submit')
    def test_register_post_with_mismatched_passwords_shows_error(self, mock_submit):
        mock_submit.return_value = captcha_success_response()
        response = self.client.post('/register/', self._valid_data(password2='MismatchPass123!'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/register.html')
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='newtester').exists())


class LoginRateLimitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ratelimited', password='testpass123')

    def test_rate_limit_after_max_attempts(self):
        """After 5 failed attempts, login is blocked."""
        from django.core.cache import cache
        cache.clear()
        for _ in range(5):
            response = self.client.post('/login', {'username': 'ratelimited', 'password': 'wrong'})
            self.assertEqual(response.status_code, 200)
        response = self.client.post('/login', {'username': 'ratelimited', 'password': 'testpass123'})
        self.assertContains(response, 'Too many login attempts')

    def test_successful_login_resets_counter(self):
        """Successful login clears the rate limit counter."""
        from django.core.cache import cache
        cache.clear()
        for _ in range(3):
            self.client.post('/login', {'username': 'ratelimited', 'password': 'wrong'})
        response = self.client.post('/login', {'username': 'ratelimited', 'password': 'testpass123'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.get('/logout')
        cache_key = 'login_attempts_127.0.0.1'
        self.assertEqual(cache.get(cache_key, 0), 0)


class MarkProcessViewTest(TestCase):
    """Tests for the mark_process POST flow."""

    def setUp(self):
        self.user = User.objects.create_user('tommy', 'tommy@test.com', 'pass')

    def _post_mark(self, data, use_captcha=False):
        """Helper to POST to mark endpoint."""
        url = '/mark_captcha/' if use_captcha else '/mark/'
        if not use_captcha:
            self.client.force_login(self.user)
        return self.client.post(url, data)

    @patch('duck.marker.email_duck_location')
    def test_mark_creates_new_duck_and_redirects(self, mock_email):
        data = {
            'duck_id': '100',
            'name': 'New Duckie',
            'location': 'Austin, TX',
            'lat': '30.2672',
            'lng': '-97.7431',
            'date_time': '01/15/2023 10:00:00',
            'comments': 'Hello world',
            'g-recaptcha-response': 'PASSED',
        }
        self.client.force_login(self.user)
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/location/', response.url)

        # Verify duck was created
        duck = Duck.objects.get(pk=100)
        self.assertEqual(duck.name, 'New Duckie')

        # Verify location was added (initial + new = 2)
        locations = DuckLocation.objects.filter(duck_id=100)
        self.assertEqual(locations.count(), 2)

        # Verify email was sent
        mock_email.assert_called_once()

    @patch('duck.marker.email_duck_location')
    def test_mark_existing_duck_adds_location(self, mock_email):
        # Create an existing duck with initial location
        Duck.objects.create(
            duck_id=50, name='Existing', create_time=timezone.now(),
            comments='', total_distance=0, approved='Y',
        )
        DuckLocation.objects.create(
            duck_id=50, user=self.user,
            latitude=32.95, longitude=-96.90,
            location='Dallas', date_time=timezone.now(),
            distance_to=0, approved='Y',
        )

        data = {
            'duck_id': '50',
            'name': 'Existing',
            'location': 'Houston, TX',
            'lat': '29.7604',
            'lng': '-95.3698',
            'date_time': '06/01/2023 12:00:00',
            'comments': 'Moved south',
            'g-recaptcha-response': 'PASSED',
        }
        self.client.force_login(self.user)
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)

        # Should now have 2 locations
        locations = DuckLocation.objects.filter(duck_id=50)
        self.assertEqual(locations.count(), 2)

        # Total distance should be updated
        duck = Duck.objects.get(pk=50)
        self.assertGreater(duck.total_distance, 0)

    @patch('duck.marker.email_duck_location')
    def test_mark_renames_unnamed_duck(self, mock_email):
        Duck.objects.create(
            duck_id=60, name='Unnamed', create_time=timezone.now(),
            comments='', total_distance=0, approved='Y',
        )
        DuckLocation.objects.create(
            duck_id=60, user=self.user,
            latitude=32.95, longitude=-96.90,
            location='Dallas', date_time=timezone.now(),
            distance_to=0, approved='Y',
        )

        data = {
            'duck_id': '60',
            'name': 'Newly Named',
            'location': 'Same Place',
            'lat': '32.95',
            'lng': '-96.90',
            'date_time': '06/01/2023 12:00:00',
            'comments': 'Renaming',
            'g-recaptcha-response': 'PASSED',
        }
        self.client.force_login(self.user)
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)

        duck = Duck.objects.get(pk=60)
        self.assertEqual(duck.name, 'Newly Named')

    def test_mark_invalid_form_rerenders(self):
        self.client.force_login(self.user)
        # Missing required fields
        data = {'duck_id': '', 'g-recaptcha-response': 'PASSED'}
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/mark.html')

    @patch('duck.marker.email_duck_location')
    def test_mark_new_duck_without_name_defaults_to_unnamed(self, mock_email):
        data = {
            'duck_id': '200',
            'name': '',
            'location': 'Nowhere',
            'lat': '0.0',
            'lng': '0.0',
            'date_time': '01/01/2023 00:00:00',
            'comments': 'Anonymous duck',
            'g-recaptcha-response': 'PASSED',
        }
        self.client.force_login(self.user)
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)

        duck = Duck.objects.get(pk=200)
        self.assertEqual(duck.name, 'Unnamed')


@override_settings(**TEST_RECAPTCHA_SETTINGS)
class MarkCaptchaSkipTest(TestCase):
    """Tests that authenticated users don't need captcha on /mark/."""

    def setUp(self):
        self.user = User.objects.create_user('captchatest', 'cap@test.com', 'pass')

    @patch('duck.marker.email_duck_location')
    def test_logged_in_user_can_submit_without_captcha(self, mock_email):
        """Authenticated user on /mark/ should succeed without g-recaptcha-response."""
        self.client.force_login(self.user)
        data = {
            'duck_id': '300',
            'name': 'No Captcha Duck',
            'location': 'Test City',
            'lat': '30.0',
            'lng': '-90.0',
            'date_time': '01/01/2023 12:00:00',
            'comments': 'No captcha needed',
        }
        response = self.client.post('/mark/', data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/location/', response.url)

        duck = Duck.objects.get(pk=300)
        self.assertEqual(duck.name, 'No Captcha Duck')

    def test_anonymous_user_mark_page_shows_captcha(self):
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recaptcha')

    def test_mark_page_has_no_captcha_field_for_logged_in_user(self):
        """GET /mark/ for logged-in user should not render captcha widget."""
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'g-recaptcha-response')

    def test_mark_captcha_redirects(self):
        response = self.client.get('/mark_captcha/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/mark/')
