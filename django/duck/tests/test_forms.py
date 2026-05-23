"""Tests for DuckForm validation."""
from django.test import TestCase, override_settings

from duck.forms import DuckForm


@override_settings(
    RECAPTCHA_PUBLIC_KEY='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    RECAPTCHA_PRIVATE_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    SILENCED_SYSTEM_CHECKS=['django_recaptcha.recaptcha_test_key_error'],
)
class DuckFormTest(TestCase):
    def _valid_data(self, **overrides):
        data = {
            'duck_id': '5',
            'name': 'Test Duck',
            'location': 'Austin, TX',
            'lat': '30.2672',
            'lng': '-97.7431',
            'date_time': '01/15/2023 10:00:00',
            'comments': 'A comment',
            'g-recaptcha-response': 'PASSED',
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = DuckForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_duck_id_required(self):
        form = DuckForm(data=self._valid_data(duck_id=''))
        self.assertFalse(form.is_valid())
        self.assertIn('duck_id', form.errors)

    def test_duck_id_min_value(self):
        form = DuckForm(data=self._valid_data(duck_id='1'))
        self.assertFalse(form.is_valid())
        self.assertIn('duck_id', form.errors)

    def test_duck_id_max_value(self):
        form = DuckForm(data=self._valid_data(duck_id='3001'))
        self.assertFalse(form.is_valid())
        self.assertIn('duck_id', form.errors)

    def test_name_optional(self):
        form = DuckForm(data=self._valid_data(name=''))
        self.assertTrue(form.is_valid(), form.errors)

    def test_location_required(self):
        form = DuckForm(data=self._valid_data(location=''))
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)

    def test_lat_required(self):
        form = DuckForm(data=self._valid_data(lat=''))
        self.assertFalse(form.is_valid())
        self.assertIn('lat', form.errors)

    def test_lng_required(self):
        form = DuckForm(data=self._valid_data(lng=''))
        self.assertFalse(form.is_valid())
        self.assertIn('lng', form.errors)

    def test_date_time_required(self):
        form = DuckForm(data=self._valid_data(date_time=''))
        self.assertFalse(form.is_valid())
        self.assertIn('date_time', form.errors)

    def test_comments_required(self):
        form = DuckForm(data=self._valid_data(comments=''))
        self.assertFalse(form.is_valid())
        self.assertIn('comments', form.errors)

    def test_image_optional(self):
        form = DuckForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_lat_must_be_numeric(self):
        form = DuckForm(data=self._valid_data(lat='not-a-number'))
        self.assertFalse(form.is_valid())
        self.assertIn('lat', form.errors)

    def test_lng_must_be_numeric(self):
        form = DuckForm(data=self._valid_data(lng='abc'))
        self.assertFalse(form.is_valid())
        self.assertIn('lng', form.errors)

    def test_invalid_date_format(self):
        form = DuckForm(data=self._valid_data(date_time='not-a-date'))
        self.assertFalse(form.is_valid())
        self.assertIn('date_time', form.errors)


@override_settings(
    RECAPTCHA_PUBLIC_KEY='6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
    RECAPTCHA_PRIVATE_KEY='6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe',
    SILENCED_SYSTEM_CHECKS=['django_recaptcha.recaptcha_test_key_error'],
)
class DuckFormCaptchaTest(TestCase):
    """Tests for require_captcha kwarg behavior."""

    def _valid_data(self, **overrides):
        data = {
            'duck_id': '5',
            'name': 'Test Duck',
            'location': 'Austin, TX',
            'lat': '30.2672',
            'lng': '-97.7431',
            'date_time': '01/15/2023 10:00:00',
            'comments': 'A comment',
        }
        data.update(overrides)
        return data

    def test_captcha_field_present_by_default(self):
        form = DuckForm()
        self.assertIn('captcha', form.fields)

    def test_captcha_field_present_when_required(self):
        form = DuckForm(require_captcha=True)
        self.assertIn('captcha', form.fields)

    def test_captcha_field_removed_when_not_required(self):
        form = DuckForm(require_captcha=False)
        self.assertNotIn('captcha', form.fields)

    def test_form_valid_without_captcha_response_when_not_required(self):
        """Form should validate without g-recaptcha-response when captcha is disabled."""
        form = DuckForm(data=self._valid_data(), require_captcha=False)
        self.assertTrue(form.is_valid(), form.errors)

    def test_form_invalid_without_captcha_response_when_required(self):
        """Form should fail validation without g-recaptcha-response when captcha is required."""
        form = DuckForm(data=self._valid_data(), require_captcha=True)
        self.assertFalse(form.is_valid())
        self.assertIn('captcha', form.errors)
