"""Tests for LinkedIn token admin refresh flow."""
import os
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings


@override_settings(
    LI_CLIENT_ID='client-id',
    LI_CLIENT_SECRET='client-secret',
    LI_API_VERSION='202504',
)
class LinkedInTokenAdminViewTest(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='admin-user',
            email='admin@test.com',
            password='pass',
            is_staff=True,
            is_superuser=True,
        )
        self.regular = User.objects.create_user(
            username='normal-user',
            email='normal@test.com',
            password='pass',
            is_staff=False,
        )
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)
        self.env_path = os.path.join(self.tmp_dir.name, 'test.env')
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write("LI_ACCESS_TOKEN=old-token\n")

    @patch.dict(os.environ, {'ENV_FILE': 'test.env'}, clear=False)
    @override_settings(PROJECT_ROOT='')
    def test_admin_page_requires_staff(self):
        self.client.force_login(self.regular)
        response = self.client.get('/admin/linkedin-token')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    @patch.dict(os.environ, {'ENV_FILE': 'test.env'}, clear=False)
    @override_settings(PROJECT_ROOT='')
    def test_admin_page_renders_for_staff(self):
        with self.settings(PROJECT_ROOT=self.tmp_dir.name):
            self.client.force_login(self.staff)
            response = self.client.get('/admin/linkedin-token')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Refresh LinkedIn Token')
        self.assertContains(response, 'http://localhost:8042/auth/linkedin/callback')

    @patch('duck.views.linkedin_fetch_person_urn', return_value='urn:li:person:abc123')
    @patch('duck.views.linkedin_refresh_access_token')
    @patch.dict(os.environ, {'ENV_FILE': 'test.env'}, clear=False)
    def test_refresh_uses_refresh_token_and_updates_env(self, mock_refresh, mock_person_urn):
        mock_refresh.return_value = {
            'access_token': 'new-access-token',
            'refresh_token': 'new-refresh-token',
            'expires_in': 5184000,
        }
        with self.settings(PROJECT_ROOT=self.tmp_dir.name, LI_REFRESH_TOKEN='existing-refresh-token'):
            self.client.force_login(self.staff)
            response = self.client.post('/admin/linkedin-token/refresh')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/linkedin-token')
        mock_refresh.assert_called_once_with('existing-refresh-token', 'client-id', 'client-secret')
        mock_person_urn.assert_called_once()

        with open(self.env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('LI_ACCESS_TOKEN=new-access-token', content)
        self.assertIn('LI_REFRESH_TOKEN=new-refresh-token', content)
        self.assertIn('LI_ACCESS_TOKEN_EXPIRES_IN=5184000', content)
        self.assertIn('LI_PERSON_URN=urn:li:person:abc123', content)
        self.assertEqual(os.environ.get('LI_ACCESS_TOKEN'), 'new-access-token')

    @patch('duck.views.build_linkedin_authorize_url', return_value='https://www.linkedin.com/oauth/v2/authorization?mock=1')
    @patch.dict(os.environ, {'ENV_FILE': 'test.env'}, clear=False)
    def test_refresh_starts_oauth_when_no_refresh_token(self, mock_auth_url):
        with self.settings(PROJECT_ROOT=self.tmp_dir.name, LI_REFRESH_TOKEN=''):
            self.client.force_login(self.staff)
            response = self.client.post('/admin/linkedin-token/refresh')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://www.linkedin.com/oauth/v2/authorization?mock=1')
        self.assertIn('linkedin_oauth_state', self.client.session)
        mock_auth_url.assert_called_once()

    @patch('duck.views.linkedin_fetch_person_urn', return_value='urn:li:person:xyz789')
    @patch('duck.views.linkedin_exchange_code_for_token')
    @patch.dict(os.environ, {'ENV_FILE': 'test.env'}, clear=False)
    def test_callback_exchanges_code_and_updates_env(self, mock_exchange, mock_person_urn):
        mock_exchange.return_value = {
            'access_token': 'callback-access-token',
            'refresh_token': 'callback-refresh-token',
            'expires_in': 5184000,
        }

        with self.settings(PROJECT_ROOT=self.tmp_dir.name):
            self.client.force_login(self.staff)
            session = self.client.session
            session['linkedin_oauth_state'] = 'state-123'
            session.save()
            response = self.client.get('/admin/linkedin-token/callback?code=abc&state=state-123')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/linkedin-token')
        mock_exchange.assert_called_once()
        mock_person_urn.assert_called_once()

        with open(self.env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('LI_ACCESS_TOKEN=callback-access-token', content)
        self.assertIn('LI_REFRESH_TOKEN=callback-refresh-token', content)

    @patch('duck.views.linkedin_exchange_code_for_token')
    def test_callback_rejects_state_mismatch(self, mock_exchange):
        self.client.force_login(self.staff)
        session = self.client.session
        session['linkedin_oauth_state'] = 'state-expected'
        session.save()

        response = self.client.get('/admin/linkedin-token/callback?code=abc&state=state-wrong')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/linkedin-token')
        mock_exchange.assert_not_called()
