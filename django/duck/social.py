"""
Social media sharing for duck sightings.

Extensible architecture: each platform is a provider class implementing
`share_sighting(duck_location)`. New platforms (TikTok, LinkedIn) can be
added by creating a new provider class and registering it in SOCIAL_PROVIDERS.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SocialShareError(Exception):
    """Raised when a social media share fails."""
    pass


class BaseSocialProvider:
    """Base class for social media providers."""
    name = 'base'

    def is_configured(self):
        """Return True if this provider has the required credentials."""
        return False

    def share_sighting(self, duck_location, photo_url=None):
        """
        Share a duck sighting to this platform.

        Args:
            duck_location: DuckLocation instance
            photo_url: Public URL to the sighting photo (optional)

        Returns:
            dict with at minimum {'success': bool, 'post_id': str|None}
        """
        raise NotImplementedError

    def _build_caption(self, duck_location):
        """Build a caption string for the sighting."""
        duck = duck_location.duck
        caption = f"Duck #{duck.duck_id} spotted"
        if duck_location.location:
            caption += f" in {duck_location.location}"
        caption += "!"
        if duck_location.comments:
            caption += f" {duck_location.comments}"
        return caption


class FacebookProvider(BaseSocialProvider):
    """Post sightings to a Facebook Page."""
    name = 'facebook'

    def is_configured(self):
        return bool(
            getattr(settings, 'FB_PAGE_ID', '') and
            getattr(settings, 'FB_PAGE_ACCESS_TOKEN', '')
        )

    def share_sighting(self, duck_location, photo_url=None):
        page_id = settings.FB_PAGE_ID
        token = settings.FB_PAGE_ACCESS_TOKEN
        caption = self._build_caption(duck_location)

        if photo_url:
            resp = requests.post(
                f"https://graph.facebook.com/v25.0/{page_id}/photos",
                data={"url": photo_url, "caption": caption, "access_token": token},
                timeout=30,
            )
        else:
            resp = requests.post(
                f"https://graph.facebook.com/v25.0/{page_id}/feed",
                data={"message": caption, "access_token": token},
                timeout=30,
            )

        data = resp.json()
        if 'error' in data:
            raise SocialShareError(f"Facebook: {data['error'].get('message', 'Unknown error')}")

        return {'success': True, 'post_id': data.get('id') or data.get('post_id')}


class InstagramProvider(BaseSocialProvider):
    """Post sightings to Instagram (Professional account required)."""
    name = 'instagram'

    def is_configured(self):
        return bool(
            getattr(settings, 'IG_USER_ID', '') and
            getattr(settings, 'IG_ACCESS_TOKEN', '')
        )

    def share_sighting(self, duck_location, photo_url=None):
        if not photo_url:
            raise SocialShareError("Instagram requires a photo URL")

        ig_user_id = settings.IG_USER_ID
        token = settings.IG_ACCESS_TOKEN
        caption = self._build_caption(duck_location)

        # Step 1: Create media container
        container_resp = requests.post(
            f"https://graph.instagram.com/v25.0/{ig_user_id}/media",
            data={"image_url": photo_url, "caption": caption, "access_token": token},
            timeout=30,
        )
        container_data = container_resp.json()
        if 'error' in container_data:
            raise SocialShareError(f"Instagram container: {container_data['error'].get('message')}")

        container_id = container_data['id']

        # Step 2: Publish
        publish_resp = requests.post(
            f"https://graph.instagram.com/v25.0/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=30,
        )
        publish_data = publish_resp.json()
        if 'error' in publish_data:
            raise SocialShareError(f"Instagram publish: {publish_data['error'].get('message')}")

        return {'success': True, 'post_id': publish_data.get('id')}


# Registry of available providers
PROVIDERS = {
    'facebook': FacebookProvider(),
    'instagram': InstagramProvider(),
}


def get_configured_providers():
    """Return list of providers that have valid credentials configured."""
    return [p for p in PROVIDERS.values() if p.is_configured()]


def share_to_all(duck_location, photo_url=None):
    """
    Share a sighting to all configured social media platforms.

    Returns:
        dict mapping provider name to result dict or error string
    """
    results = {}
    for provider in get_configured_providers():
        try:
            results[provider.name] = provider.share_sighting(duck_location, photo_url)
        except SocialShareError as e:
            logger.error("Social share failed for %s: %s", provider.name, e)
            results[provider.name] = {'success': False, 'error': str(e)}
        except Exception as e:
            logger.exception("Unexpected error sharing to %s", provider.name)
            results[provider.name] = {'success': False, 'error': str(e)}
    return results


def share_to(platform, duck_location, photo_url=None):
    """
    Share a sighting to a specific platform.

    Args:
        platform: Provider name string (e.g., 'facebook', 'instagram')
        duck_location: DuckLocation instance
        photo_url: Public URL to the photo

    Returns:
        dict with {'success': bool, ...}

    Raises:
        SocialShareError if the platform is not configured or share fails
    """
    provider = PROVIDERS.get(platform)
    if not provider:
        raise SocialShareError(f"Unknown platform: {platform}")
    if not provider.is_configured():
        raise SocialShareError(f"{platform} is not configured (missing credentials)")
    return provider.share_sighting(duck_location, photo_url)
