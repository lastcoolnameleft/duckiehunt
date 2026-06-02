"""Tests for the social media sharing module."""
from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.utils import timezone

from duck.models import Duck, DuckLocation
from duck.social import (
    BaseSocialProvider,
    FacebookProvider,
    InstagramProvider,
    SocialShareError,
    get_configured_providers,
    share_to,
    share_to_all,
)


class TestBaseSocialProvider(TestCase):
    def test_is_configured_returns_false(self):
        provider = BaseSocialProvider()
        self.assertFalse(provider.is_configured())

    def test_share_sighting_raises_not_implemented(self):
        provider = BaseSocialProvider()
        with self.assertRaises(NotImplementedError):
            provider.share_sighting(None)


class TestBuildCaption(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(create_time=timezone.now(), comments='', duck_id=99999, name='Test Duck')
        self.location = DuckLocation.objects.create(
            duck=self.duck,
            location='Austin, TX',
            comments='Found at the park',
        )

    def tearDown(self):
        self.duck.delete()

    def test_caption_with_location_and_comments(self):
        provider = FacebookProvider()
        caption = provider._build_caption(self.location)
        self.assertEqual(caption, 'Duck #99999 spotted in Austin, TX! Found at the park')

    def test_caption_without_location(self):
        self.location.location = ''
        self.location.save()
        provider = FacebookProvider()
        caption = provider._build_caption(self.location)
        self.assertEqual(caption, 'Duck #99999 spotted! Found at the park')

    def test_caption_without_comments(self):
        self.location.comments = ''
        self.location.save()
        provider = FacebookProvider()
        caption = provider._build_caption(self.location)
        self.assertEqual(caption, 'Duck #99999 spotted in Austin, TX!')

    def test_caption_minimal(self):
        self.location.location = ''
        self.location.comments = ''
        self.location.save()
        provider = FacebookProvider()
        caption = provider._build_caption(self.location)
        self.assertEqual(caption, 'Duck #99999 spotted!')


@override_settings(FB_PAGE_ID='', FB_PAGE_ACCESS_TOKEN='')
class TestFacebookProviderNotConfigured(TestCase):
    def test_is_configured_without_credentials(self):
        provider = FacebookProvider()
        self.assertFalse(provider.is_configured())


@override_settings(FB_PAGE_ID='123456', FB_PAGE_ACCESS_TOKEN='fake_token')
class TestFacebookProviderConfigured(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(create_time=timezone.now(), comments='', duck_id=99998, name='FB Duck')
        self.location = DuckLocation.objects.create(
            duck=self.duck,
            location='Seattle, WA',
            comments='Near the market',
        )

    def tearDown(self):
        self.duck.delete()

    def test_is_configured_with_credentials(self):
        provider = FacebookProvider()
        self.assertTrue(provider.is_configured())

    @patch('duck.social.requests.post')
    def test_share_text_post(self, mock_post):
        mock_post.return_value = MagicMock(
            json=lambda: {'id': '123456_789'}
        )
        provider = FacebookProvider()
        result = provider.share_sighting(self.location)
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], '123456_789')
        mock_post.assert_called_once()

    @patch('duck.social.requests.post')
    def test_share_with_photo(self, mock_post):
        mock_post.return_value = MagicMock(
            json=lambda: {'id': '123456_photo'}
        )
        provider = FacebookProvider()
        result = provider.share_sighting(self.location, photo_url='https://example.com/duck.jpg')
        self.assertTrue(result['success'])
        call_data = mock_post.call_args[1]['data']
        self.assertIn('url', call_data)
        self.assertEqual(call_data['url'], 'https://example.com/duck.jpg')

    @patch('duck.social.requests.post')
    def test_share_error(self, mock_post):
        mock_post.return_value = MagicMock(
            json=lambda: {'error': {'message': 'Token expired'}}
        )
        provider = FacebookProvider()
        with self.assertRaises(SocialShareError):
            provider.share_sighting(self.location)


@override_settings(IG_USER_ID='', IG_ACCESS_TOKEN='')
class TestInstagramProviderNotConfigured(TestCase):
    def test_is_configured_without_credentials(self):
        provider = InstagramProvider()
        self.assertFalse(provider.is_configured())


@override_settings(IG_USER_ID='ig_123', IG_ACCESS_TOKEN='ig_token')
class TestInstagramProvider(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(create_time=timezone.now(), comments='', duck_id=99997, name='IG Duck')
        self.location = DuckLocation.objects.create(
            duck=self.duck,
            location='Portland, OR',
        )

    def tearDown(self):
        self.duck.delete()

    def test_requires_photo(self):
        provider = InstagramProvider()
        with self.assertRaises(SocialShareError):
            provider.share_sighting(self.location, photo_url=None)

    @patch('duck.social.requests.post')
    def test_two_step_publish(self, mock_post):
        mock_post.side_effect = [
            MagicMock(json=lambda: {'id': 'container_123'}),
            MagicMock(json=lambda: {'id': 'media_456'}),
        ]
        provider = InstagramProvider()
        result = provider.share_sighting(self.location, photo_url='https://example.com/duck.jpg')
        self.assertTrue(result['success'])
        self.assertEqual(result['post_id'], 'media_456')
        self.assertEqual(mock_post.call_count, 2)


@override_settings(
    FB_PAGE_ID='', FB_PAGE_ACCESS_TOKEN='',
    IG_USER_ID='', IG_ACCESS_TOKEN='',
)
class TestGetConfiguredProviders(TestCase):
    def test_no_providers_configured(self):
        providers = get_configured_providers()
        self.assertEqual(len(providers), 0)


@override_settings(
    FB_PAGE_ID='123', FB_PAGE_ACCESS_TOKEN='token',
    IG_USER_ID='', IG_ACCESS_TOKEN='',
)
class TestShareTo(TestCase):
    def setUp(self):
        self.duck = Duck.objects.create(create_time=timezone.now(), comments='', duck_id=99996, name='Share Duck')
        self.location = DuckLocation.objects.create(duck=self.duck)

    def tearDown(self):
        self.duck.delete()

    def test_share_to_unknown_platform(self):
        with self.assertRaises(SocialShareError):
            share_to('tiktok', self.location)

    def test_share_to_unconfigured_platform(self):
        with self.assertRaises(SocialShareError):
            share_to('instagram', self.location)

    @patch('duck.social.requests.post')
    def test_share_to_all_catches_errors(self, mock_post):
        mock_post.return_value = MagicMock(
            json=lambda: {'error': {'message': 'fail'}}
        )
        results = share_to_all(self.location)
        self.assertIn('facebook', results)
        self.assertFalse(results['facebook']['success'])
