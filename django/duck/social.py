"""
Social media sharing for duck sightings.

Extensible architecture: each platform is a provider class implementing
`share_sighting(duck_location)`. New platforms (TikTok, LinkedIn) can be
added by creating a new provider class and registering it in SOCIAL_PROVIDERS.
"""
import logging

import requests
from requests_oauthlib import OAuth2Session
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
            f"https://graph.facebook.com/v25.0/{ig_user_id}/media",
            data={"image_url": photo_url, "caption": caption, "access_token": token},
            timeout=30,
        )
        container_data = container_resp.json()
        if 'error' in container_data:
            raise SocialShareError(f"Instagram container: {container_data['error'].get('message')}")

        container_id = container_data['id']

        # Step 2: Publish
        publish_resp = requests.post(
            f"https://graph.facebook.com/v25.0/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": token},
            timeout=30,
        )
        publish_data = publish_resp.json()
        if 'error' in publish_data:
            raise SocialShareError(f"Instagram publish: {publish_data['error'].get('message')}")

        return {'success': True, 'post_id': publish_data.get('id')}


class LinkedInProvider(BaseSocialProvider):
    """Post sightings to LinkedIn personal or organization feed."""
    name = 'linkedin'

    def is_configured(self):
        return bool(getattr(settings, 'LI_ACCESS_TOKEN', '') and self._author_urn())

    def _author_urn(self):
        return (
            getattr(settings, 'LI_AUTHOR_URN', '')
            or getattr(settings, 'LI_PERSON_URN', '')
            or getattr(settings, 'LI_ORGANIZATION_URN', '')
        )

    def _oauth_session(self):
        return OAuth2Session(
            token={
                'access_token': settings.LI_ACCESS_TOKEN,
                'token_type': 'Bearer',
            }
        )

    def _linkedin_headers(self):
        headers = {
            'X-Restli-Protocol-Version': '2.0.0',
        }
        version = getattr(settings, 'LI_API_VERSION', '')
        if version:
            headers['LinkedIn-Version'] = version
        return headers

    def _response_json(self, response):
        try:
            return response.json()
        except ValueError:
            return {}

    def _error_message(self, response, fallback='Unknown LinkedIn API error'):
        data = self._response_json(response)
        if isinstance(data, dict):
            for key in ('message', 'error_description', 'error'):
                value = data.get(key)
                if value:
                    return str(value)
        text = (response.text or '').strip()
        return text[:500] if text else fallback

    def _upload_image(self, session, photo_url):
        image_resp = requests.get(photo_url, timeout=30)
        if not image_resp.ok:
            raise SocialShareError(
                f"LinkedIn image download failed ({image_resp.status_code}): "
                f"{self._error_message(image_resp, 'could not download photo URL')}"
            )

        owner = self._author_urn()
        init_resp = session.post(
            'https://api.linkedin.com/rest/images?action=initializeUpload',
            json={'initializeUploadRequest': {'owner': owner}},
            headers=self._linkedin_headers(),
            timeout=30,
        )
        if not init_resp.ok:
            raise SocialShareError(
                f"LinkedIn initializeUpload failed ({init_resp.status_code}): "
                f"{self._error_message(init_resp)}"
            )

        init_data = self._response_json(init_resp)
        upload_data = init_data.get('value', {}) if isinstance(init_data, dict) else {}
        upload_url = upload_data.get('uploadUrl')
        image_urn = upload_data.get('image')
        if not upload_url or not image_urn:
            raise SocialShareError("LinkedIn initializeUpload response missing uploadUrl or image URN")

        upload_headers = {'Content-Type': image_resp.headers.get('Content-Type', 'application/octet-stream')}
        put_resp = session.put(upload_url, data=image_resp.content, headers=upload_headers, timeout=30)
        if not put_resp.ok:
            raise SocialShareError(
                f"LinkedIn image PUT failed ({put_resp.status_code}): "
                f"{self._error_message(put_resp, 'upload failed')}"
            )

        return image_urn

    def share_sighting(self, duck_location, photo_url=None):
        if not self.is_configured():
            raise SocialShareError("LinkedIn is not configured (missing token or author URN)")

        caption = self._build_caption(duck_location)
        session = self._oauth_session()

        payload = {
            'author': self._author_urn(),
            'commentary': caption,
            'visibility': 'PUBLIC',
            'distribution': {
                'feedDistribution': 'MAIN_FEED',
                'targetEntities': [],
                'thirdPartyDistributionChannels': [],
            },
            'lifecycleState': 'PUBLISHED',
            'isReshareDisabledByAuthor': False,
        }
        if photo_url:
            image_urn = self._upload_image(session, photo_url)
            payload['content'] = {'media': {'id': image_urn}}

        post_resp = session.post(
            'https://api.linkedin.com/rest/posts',
            json=payload,
            headers=self._linkedin_headers(),
            timeout=30,
        )
        if not post_resp.ok:
            raise SocialShareError(
                f"LinkedIn post failed ({post_resp.status_code}): {self._error_message(post_resp)}"
            )

        post_data = self._response_json(post_resp)
        post_id = None
        if isinstance(post_data, dict):
            post_id = post_data.get('id')
        post_id = post_id or post_resp.headers.get('x-restli-id')

        return {'success': True, 'post_id': post_id}


# Registry of available providers
PROVIDERS = {
    'facebook': FacebookProvider(),
    'instagram': InstagramProvider(),
    'linkedin': LinkedInProvider(),
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
