"""Tests for duck views (page rendering, auth, redirects)"""
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone

from duck.models import Duck, DuckLocation, DuckLocationPhoto


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

    def test_mark_redirects_anonymous(self):
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)

    def test_mark_accessible_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/mark.html')

    def test_mark_with_duck_id_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get('/mark/5')
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_mark_captcha_accessible_without_login(self):
        response = self.client.get('/mark_captcha/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/mark.html')

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/login.html')

    def test_login_page_parses_next_param(self):
        response = self.client.get('/login?next=/mark/42')
        self.assertEqual(response.context['duck_id'], '42')

    def test_login_page_no_next(self):
        response = self.client.get('/login')
        self.assertIsNone(response.context['duck_id'])

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


@override_settings(
    RECAPTCHA_PUBLIC_KEY='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    RECAPTCHA_PRIVATE_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    SILENCED_SYSTEM_CHECKS=['django_recaptcha.recaptcha_test_key_error'],
)
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

    def test_anonymous_user_fails_without_captcha(self):
        """Anonymous user on /mark_captcha/ should fail without g-recaptcha-response."""
        data = {
            'duck_id': '301',
            'name': 'Captcha Duck',
            'location': 'Test City',
            'lat': '30.0',
            'lng': '-90.0',
            'date_time': '01/01/2023 12:00:00',
            'comments': 'Should fail',
        }
        response = self.client.post('/mark_captcha/', data)
        # Should re-render form (not redirect) due to captcha failure
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'duck/mark.html')
        self.assertFalse(Duck.objects.filter(pk=301).exists())

    @patch('duck.marker.email_duck_location')
    def test_anonymous_user_succeeds_with_captcha(self, mock_email):
        """Anonymous user on /mark_captcha/ should succeed with valid captcha response."""
        data = {
            'duck_id': '302',
            'name': 'Captcha OK Duck',
            'location': 'Test City',
            'lat': '30.0',
            'lng': '-90.0',
            'date_time': '01/01/2023 12:00:00',
            'comments': 'Captcha passed',
            'g-recaptcha-response': 'PASSED',
        }
        response = self.client.post('/mark_captcha/', data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/location/', response.url)

    def test_mark_page_has_no_captcha_field_for_logged_in_user(self):
        """GET /mark/ for logged-in user should not render captcha widget."""
        self.client.force_login(self.user)
        response = self.client.get('/mark/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'g-recaptcha-response')

    def test_mark_captcha_page_has_captcha_field(self):
        """GET /mark_captcha/ should render captcha widget."""
        response = self.client.get('/mark_captcha/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'recaptcha')
