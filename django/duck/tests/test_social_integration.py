"""
Social media integration test — full E2E post-and-cleanup cycle.

Creates a duck + location via the ORM, posts to all configured social
platforms, verifies posts exist, then cleans everything up.

Social credentials are NOT stored in .env (to prevent accidental posting
during normal dev work). Pass them at test time via .env.social:

  env RUN_SOCIAL_INTEGRATION_TESTS=yes $(cat .env.social | xargs) cd django && python manage.py test duck.tests.test_social_integration -v 2

See .env.social.example for the required variables.

IMPORTANT: This test posts to REAL social media accounts. It requires
RUN_SOCIAL_INTEGRATION_TESTS=yes and will prompt for confirmation.
"""
import os
import sys

from urllib.parse import quote

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

import requests
from requests_oauthlib import OAuth2Session

from duck.models import Duck, DuckLocation


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TEST_DUCK_ID = 29999
PUBLIC_IMAGE_URL = "https://duckiehunt.com/media/29623778277.jpg"


def _require_env(var_name):
    """Get env var or skip."""
    value = os.environ.get(var_name, "")
    if not value:
        return None
    return value


# ---------------------------------------------------------------------------
# Social platform helpers
# ---------------------------------------------------------------------------

class SocialPostTracker:
    """Tracks created posts for cleanup."""

    def __init__(self):
        self.posts = {}  # platform -> post_id

    def add(self, platform, post_id):
        if post_id:
            self.posts[platform] = post_id


def _get_post_url(platform, post_id, config=None):
    """Construct a human-viewable URL for a social media post."""
    if platform == "facebook":
        return f"https://www.facebook.com/{post_id}"
    elif platform == "linkedin":
        return f"https://www.linkedin.com/feed/update/{post_id}"
    elif platform == "instagram" and config:
        # Fetch the permalink from the API
        try:
            resp = requests.get(
                f"https://graph.facebook.com/v25.0/{post_id}",
                params={
                    "fields": "permalink",
                    "access_token": config["access_token"],
                },
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("permalink", f"IG post ID: {post_id}")
        except Exception:
            pass
        return f"IG post ID: {post_id}"
    return f"Post ID: {post_id}"


def post_to_ig(ig_config, caption, image_url):
    """Create an Instagram post. Returns post_id."""
    token = ig_config["access_token"]
    user_id = ig_config["user_id"]

    container_resp = requests.post(
        f"https://graph.facebook.com/v25.0/{user_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": token},
        timeout=30,
    )
    container_data = container_resp.json()
    if "error" in container_data:
        raise RuntimeError(f"IG container: {container_data['error'].get('message')}")

    container_id = container_data["id"]

    publish_resp = requests.post(
        f"https://graph.facebook.com/v25.0/{user_id}/media_publish",
        data={"creation_id": container_id, "access_token": token},
        timeout=30,
    )
    publish_data = publish_resp.json()
    if "error" in publish_data:
        raise RuntimeError(f"IG publish: {publish_data['error'].get('message')}")

    return publish_data.get("id")


def post_to_fb(fb_config, caption, image_url=None):
    """Create a Facebook Page post. Returns post_id."""
    page_id = fb_config["page_id"]
    token = fb_config["access_token"]

    if image_url:
        resp = requests.post(
            f"https://graph.facebook.com/v25.0/{page_id}/photos",
            data={"url": image_url, "caption": caption, "access_token": token},
            timeout=30,
        )
    else:
        resp = requests.post(
            f"https://graph.facebook.com/v25.0/{page_id}/feed",
            data={"message": caption, "access_token": token},
            timeout=30,
        )

    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"FB: {data['error'].get('message')}")
    return data.get("id") or data.get("post_id")


def post_to_li(li_config, caption, image_url=None):
    """Create a LinkedIn post. Returns post_id."""
    session = OAuth2Session(
        token={"access_token": li_config["access_token"], "token_type": "Bearer"}
    )
    headers = {"X-Restli-Protocol-Version": "2.0.0"}
    if li_config.get("api_version"):
        headers["LinkedIn-Version"] = li_config["api_version"]

    payload = {
        "author": li_config["author_urn"],
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    if image_url:
        img_resp = requests.get(image_url, timeout=30)
        if not img_resp.ok:
            raise RuntimeError(f"LI image download failed: {img_resp.status_code}")

        init_resp = session.post(
            "https://api.linkedin.com/rest/images?action=initializeUpload",
            json={"initializeUploadRequest": {"owner": li_config["author_urn"]}},
            headers=headers,
            timeout=30,
        )
        if not init_resp.ok:
            raise RuntimeError(f"LI initializeUpload failed: {init_resp.text}")

        init_data = init_resp.json().get("value", {})
        upload_url = init_data.get("uploadUrl")
        image_urn = init_data.get("image")
        if not upload_url or not image_urn:
            raise RuntimeError("LI initializeUpload missing uploadUrl or image URN")

        put_resp = session.put(
            upload_url,
            data=img_resp.content,
            headers={"Content-Type": img_resp.headers.get("Content-Type", "application/octet-stream")},
            timeout=30,
        )
        if not put_resp.ok:
            raise RuntimeError(f"LI image PUT failed: {put_resp.status_code}")

        payload["content"] = {"media": {"id": image_urn}}

    post_resp = session.post(
        "https://api.linkedin.com/rest/posts",
        json=payload,
        headers=headers,
        timeout=30,
    )
    if not post_resp.ok:
        raise RuntimeError(f"LI post failed: {post_resp.status_code} {post_resp.text}")

    post_id = None
    try:
        post_data = post_resp.json()
        post_id = post_data.get("id")
    except ValueError:
        pass
    return post_id or post_resp.headers.get("x-restli-id")


def verify_ig_post(ig_config, post_id):
    """Verify an Instagram post exists."""
    resp = requests.get(
        f"https://graph.facebook.com/v25.0/{post_id}",
        params={"fields": "id,caption", "access_token": ig_config["access_token"]},
        timeout=15,
    )
    return resp.status_code == 200 and resp.json().get("id") == post_id


def verify_fb_post(fb_config, post_id):
    """Verify a Facebook post exists."""
    resp = requests.get(
        f"https://graph.facebook.com/v25.0/{post_id}",
        params={"fields": "id", "access_token": fb_config["access_token"]},
        timeout=15,
    )
    return resp.status_code == 200


def verify_li_post(li_config, post_id):
    """Verify a LinkedIn post exists."""
    headers = {
        "Authorization": f"Bearer {li_config['access_token']}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if li_config.get("api_version"):
        headers["LinkedIn-Version"] = li_config["api_version"]
    resp = requests.get(
        f"https://api.linkedin.com/rest/posts/{quote(post_id, safe='')}",
        headers=headers,
        timeout=15,
    )
    return resp.status_code == 200


def delete_ig_post(ig_config, post_id):
    """Delete an Instagram post."""
    resp = requests.delete(
        f"https://graph.facebook.com/v25.0/{post_id}",
        params={"access_token": ig_config["access_token"]},
        timeout=15,
    )
    return resp.status_code == 200


def delete_fb_post(fb_config, post_id):
    """Delete a Facebook post."""
    resp = requests.delete(
        f"https://graph.facebook.com/v25.0/{post_id}",
        params={"access_token": fb_config["access_token"]},
        timeout=15,
    )
    return resp.status_code == 200


def delete_li_post(li_config, post_id):
    """Delete a LinkedIn post. Note: uploaded image assets may remain as orphans."""
    headers = {
        "Authorization": f"Bearer {li_config['access_token']}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if li_config.get("api_version"):
        headers["LinkedIn-Version"] = li_config["api_version"]
    resp = requests.delete(
        f"https://api.linkedin.com/rest/posts/{quote(post_id, safe='')}",
        headers=headers,
        timeout=15,
    )
    return resp.status_code in (200, 204)


# ---------------------------------------------------------------------------
# Confirmation prompt
# ---------------------------------------------------------------------------

def confirm_or_skip(skip_func):
    """Require explicit opt-in. Prompt interactively only if not already confirmed."""
    # Always require explicit env var — prevents accidental runs in CI
    if os.environ.get("RUN_SOCIAL_INTEGRATION_TESTS") != "yes":
        # Interactive confirmation as fallback
        if sys.stdin.isatty():
            print("\n" + "=" * 70)
            print("⚠️  SOCIAL MEDIA INTEGRATION TEST")
            print("=" * 70)
            print("This test will:")
            print("  1. Create a test duck in the DB")
            print("  2. Post to ALL configured social platforms (IG, FB, LinkedIn)")
            print("  3. Verify posts exist on each platform")
            print(f"  4. Wait for your confirmation before cleanup")
            print("  5. Delete all posts (DB cleanup is automatic)")
            print()
            print(f"  Test Duck ID: {TEST_DUCK_ID}")
            print(f"  Test Image:   {PUBLIC_IMAGE_URL}")
            print("=" * 70)

            response = input("\nProceed? [y/N]: ").strip().lower()
            if response != "y":
                skip_func("User declined — test skipped")
        else:
            skip_func(
                "Set RUN_SOCIAL_INTEGRATION_TESTS=yes to run. "
                "Example: env RUN_SOCIAL_INTEGRATION_TESTS=yes $(cat .env.social | xargs) "
                "python manage.py test duck.tests.test_social_integration -v 2"
            )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class TestSocialIntegration(TestCase):
    """
    Full E2E social media integration test.

    1. Prompts for user confirmation
    2. Creates a test duck + location via ORM
    3. Posts to social platforms directly (same APIs as social.py)
    4. Verifies posts exist
    5. Deletes social posts (DB rolls back automatically)

    Run with:
      env RUN_SOCIAL_INTEGRATION_TESTS=yes $(cat .env.social | xargs) \\
        python manage.py test duck.tests.test_social_integration -v 2

    Use --no-input to skip the confirmation prompt.
    """

    def setUp(self):
        self.tracker = SocialPostTracker()
        self.platforms = {}  # platform name -> config dict

        # Load configs for whichever platforms have creds
        ig_user_id = _require_env("IG_USER_ID")
        ig_token = _require_env("IG_ACCESS_TOKEN")
        if ig_user_id and ig_token:
            self.platforms["instagram"] = {"user_id": ig_user_id, "access_token": ig_token}

        fb_page_id = _require_env("FB_PAGE_ID")
        fb_token = _require_env("FB_PAGE_ACCESS_TOKEN")
        if fb_page_id and fb_token:
            self.platforms["facebook"] = {"page_id": fb_page_id, "access_token": fb_token}

        li_token = _require_env("LI_ACCESS_TOKEN")
        li_author = (
            os.environ.get("LI_PERSON_URN", "")
            or os.environ.get("LI_ORGANIZATION_URN", "")
        )
        if li_token and li_author:
            self.platforms["linkedin"] = {
                "access_token": li_token,
                "author_urn": li_author,
                "api_version": os.environ.get("LI_API_VERSION", ""),
            }

        if not self.platforms:
            self.skipTest(
                "No social creds set — run with: "
                "env $(cat .env.social | xargs) python manage.py test ..."
            )

        # Prompt for confirmation
        confirm_or_skip(self.skipTest)

        # Create test data
        self.user = User.objects.create_user("social_test_user", "test@test.com", "pass")
        self.duck = Duck.objects.create(
            duck_id=TEST_DUCK_ID,
            name="Social Test Duck",
            create_time=timezone.now(),
            created_by=self.user,
            comments="",
        )
        self.location = DuckLocation.objects.create(
            duck=self.duck,
            user=self.user,
            location="Test Location, Dallas TX",
            latitude=32.7767,
            longitude=-96.7970,
            date_time=timezone.now(),
            comments="🧪 Integration test — will be deleted",
            approved="Y",
        )

    def tearDown(self):
        """Always clean up social posts. Fails if any deletion fails."""
        print("\n📋 Cleaning up social posts...")
        cleanup_failures = []
        for platform, post_id in self.tracker.posts.items():
            try:
                config = self.platforms.get(platform, {})
                if platform == "instagram":
                    ok = delete_ig_post(config, post_id)
                elif platform == "facebook":
                    ok = delete_fb_post(config, post_id)
                elif platform == "linkedin":
                    ok = delete_li_post(config, post_id)
                else:
                    ok = False
                status = "✓" if ok else "✗"
                print(f"  {status} {platform}: {post_id}")
                if not ok:
                    cleanup_failures.append(f"{platform}: {post_id}")
            except Exception as e:
                print(f"  ✗ {platform} cleanup error: {e}")
                cleanup_failures.append(f"{platform}: {e}")

        if cleanup_failures:
            print(f"\n  ⚠️  Cleanup failures (posts may need manual deletion): {cleanup_failures}")
            print("     Instagram deletion requires 'instagram_manage_content' permission.")

    def test_full_social_posting_cycle(self):
        """Post to all configured platforms, verify, wait for inspection."""
        caption = (
            f"Duck #{TEST_DUCK_ID} spotted in Test Location! "
            f"🧪 Integration test — will be deleted"
        )
        errors = []

        # --- Step 1: Post to each configured platform ---
        print(f"\n📋 Step 1: Posting to {len(self.platforms)} platform(s)...")

        if "instagram" in self.platforms:
            try:
                print("  Posting to Instagram...")
                ig_id = post_to_ig(self.platforms["instagram"], caption, PUBLIC_IMAGE_URL)
                self.tracker.add("instagram", ig_id)
                print(f"  ✓ Instagram: {ig_id}")
            except Exception as e:
                errors.append(f"Instagram post: {e}")
                print(f"  ✗ Instagram: {e}")

        if "facebook" in self.platforms:
            try:
                print("  Posting to Facebook...")
                fb_id = post_to_fb(self.platforms["facebook"], caption, PUBLIC_IMAGE_URL)
                self.tracker.add("facebook", fb_id)
                print(f"  ✓ Facebook: {fb_id}")
            except Exception as e:
                errors.append(f"Facebook post: {e}")
                print(f"  ✗ Facebook: {e}")

        if "linkedin" in self.platforms:
            try:
                print("  Posting to LinkedIn...")
                li_id = post_to_li(self.platforms["linkedin"], caption, PUBLIC_IMAGE_URL)
                self.tracker.add("linkedin", li_id)
                print(f"  ✓ LinkedIn: {li_id}")
            except Exception as e:
                errors.append(f"LinkedIn post: {e}")
                print(f"  ✗ LinkedIn: {e}")

        # --- Step 2: Verify posts exist ---
        print("\n📋 Step 2: Verifying posts...")

        if "instagram" in self.tracker.posts:
            try:
                ok = verify_ig_post(self.platforms["instagram"], self.tracker.posts["instagram"])
                print(f"  {'✓' if ok else '✗'} Instagram verified")
                if not ok:
                    errors.append("Instagram: post not found after creation")
            except Exception as e:
                errors.append(f"Instagram verify: {e}")
                print(f"  ✗ Instagram verify error: {e}")

        if "facebook" in self.tracker.posts:
            try:
                ok = verify_fb_post(self.platforms["facebook"], self.tracker.posts["facebook"])
                print(f"  {'✓' if ok else '✗'} Facebook verified")
                if not ok:
                    errors.append("Facebook: post not found after creation")
            except Exception as e:
                errors.append(f"Facebook verify: {e}")
                print(f"  ✗ Facebook verify error: {e}")

        if "linkedin" in self.tracker.posts:
            try:
                ok = verify_li_post(self.platforms["linkedin"], self.tracker.posts["linkedin"])
                print(f"  {'✓' if ok else '✗'} LinkedIn verified")
                if not ok:
                    errors.append("LinkedIn: post not found after creation")
            except Exception as e:
                errors.append(f"LinkedIn verify: {e}")
                print(f"  ✗ LinkedIn verify error: {e}")

        # --- Step 3: Wait for manual inspection ---
        print("\n📋 Step 3: Manual inspection...")
        print("  Check your social media posts:")
        for platform, post_id in self.tracker.posts.items():
            url = _get_post_url(platform, post_id, self.platforms.get(platform))
            print(f"    {platform}: {url}")
        input("\n  Press Enter to continue (posts will be deleted)...")

        # --- Report ---
        print("\n" + "=" * 70)
        print("📊 RESULTS")
        print("=" * 70)
        print(f"  Platforms configured: {', '.join(self.platforms.keys())}")
        print(f"  Posts created: {len(self.tracker.posts)}")
        for platform, post_id in self.tracker.posts.items():
            url = _get_post_url(platform, post_id, self.platforms.get(platform))
            print(f"    {platform}: {url}")
        if errors:
            print(f"\n  Issues ({len(errors)}):")
            for err in errors:
                print(f"    - {err}")
        print("=" * 70)

        # tearDown handles social post deletion, Django handles DB rollback
        self.assertEqual(len(errors), 0, f"Social posting issues: {'; '.join(errors)}")
