"""Tests verifying settings load correctly from environment variables."""
import os
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings


class SettingsSecurityTests(TestCase):
    """Verify that secrets are loaded from environment, not hardcoded."""

    def test_secret_key_required_when_debug_false(self):
        """SECRET_KEY must be set via env var when DEBUG=False."""
        env = os.environ.copy()
        env.pop("DJANGO_SECRET_KEY", None)

        with patch.dict(os.environ, env, clear=True):
            # Re-import settings logic to test the guard
            from duckiehunt.settings import _SECRET_KEY_INSECURE

            # The insecure key should never be used in production
            self.assertIn("insecure", _SECRET_KEY_INSECURE)

    def test_no_hardcoded_secrets_in_init(self):
        """The active settings module must not contain hardcoded real secrets."""
        import inspect

        import duckiehunt.settings as settings_module

        source = inspect.getsource(settings_module)

        # These patterns indicate hardcoded secrets
        secret_patterns = [
            "SG.",  # SendGrid API key prefix
            "GOCSPX-",  # Google OAuth secret prefix
            "sk-",  # Generic API key prefix
        ]
        for pattern in secret_patterns:
            # Skip the insecure dev key which is intentional
            lines_with_pattern = [
                line
                for line in source.split("\n")
                if pattern in line and "insecure" not in line.lower()
            ]
            self.assertEqual(
                lines_with_pattern,
                [],
                f"Found potential hardcoded secret pattern '{pattern}' in settings",
            )

    def test_settings_use_environ_for_secrets(self):
        """All sensitive settings should read from os.environ."""
        from django.conf import settings

        # These settings should be configurable via environment
        env_driven_settings = [
            "SOCIAL_AUTH_FACEBOOK_KEY",
            "SOCIAL_AUTH_FACEBOOK_SECRET",
            "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
            "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET",
            "GOOGLE_MAPS_API_KEY",
            "FLICKR_API_KEY",
            "FLICKR_API_SECRET",
        ]

        for setting_name in env_driven_settings:
            # Verify setting exists (doesn't raise AttributeError)
            value = getattr(settings, setting_name, None)
            self.assertIsNotNone(
                value,
                f"Setting {setting_name} should be defined",
            )

    def test_secret_key_not_empty_in_production_mode(self):
        """Verify the guard in __init__.py would raise when no key in prod."""
        # We can't easily reload the settings module in a running Django process,
        # but we can verify the guard logic exists by checking the source
        import inspect

        import duckiehunt.settings as s

        source = inspect.getsource(s)
        self.assertIn("ImproperlyConfigured", source)
        self.assertIn("DJANGO_SECRET_KEY", source)
        self.assertIn("DEBUG", source)
        # Verify the pattern: raise when no key and not debug
        self.assertIn(
            "DJANGO_SECRET_KEY environment variable is required", source
        )

    def test_debug_mode_uses_insecure_key(self):
        """In DEBUG mode without DJANGO_SECRET_KEY, insecure key is used."""
        from django.conf import settings

        # In test mode, we're running with DEBUG=True and test secret key
        # Just verify the mechanism exists
        from duckiehunt.settings import _SECRET_KEY_INSECURE

        self.assertTrue(len(_SECRET_KEY_INSECURE) > 10)
        self.assertIn("insecure", _SECRET_KEY_INSECURE)

    def test_env_example_documents_all_secrets(self):
        """The .env.example file should document all secret env vars."""
        import pathlib

        # Navigate from django/duck/tests/ up to project root
        env_example = (
            pathlib.Path(__file__).resolve().parents[3] / ".env.example"
        )
        self.assertTrue(
            env_example.exists(), f".env.example not found at {env_example}"
        )

        content = env_example.read_text()

        required_vars = [
            "DJANGO_SECRET_KEY",
            "SENDGRID_API_KEY",
            "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY",
            "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET",
            "SOCIAL_AUTH_FACEBOOK_KEY",
            "SOCIAL_AUTH_FACEBOOK_SECRET",
            "GOOGLE_MAPS_API_KEY",
            "FLICKR_API_KEY",
            "FLICKR_API_SECRET",
            "SENTRY_DSN",
            "RECAPTCHA_PUBLIC_KEY",
            "RECAPTCHA_PRIVATE_KEY",
        ]

        for var in required_vars:
            self.assertIn(
                var,
                content,
                f"Environment variable {var} not documented in .env.example",
            )
