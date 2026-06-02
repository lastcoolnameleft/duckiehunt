"""Management command to test social media posting."""
from django.core.management.base import BaseCommand, CommandError

from duck.social import (
    PROVIDERS,
    get_configured_providers,
    share_to,
    SocialShareError,
)


class Command(BaseCommand):
    help = 'Test social media posting. Posts a test message or shares a real sighting.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            help='Platform to test (facebook, instagram). Tests all configured if omitted.',
        )
        parser.add_argument(
            '--sighting',
            type=int,
            help='DuckLocation ID to share. If omitted, posts a test message.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be posted without actually posting.',
        )

    def handle(self, *args, **options):
        configured = get_configured_providers()

        if not configured:
            self.stderr.write(self.style.ERROR(
                'No social providers configured. Set FB_PAGE_ID + FB_PAGE_ACCESS_TOKEN in your environment.'
            ))
            return

        self.stdout.write(f"Configured providers: {', '.join(p.name for p in configured)}")

        platform = options['platform']
        sighting_id = options['sighting']
        dry_run = options['dry_run']

        if platform and platform not in PROVIDERS:
            raise CommandError(f"Unknown platform: {platform}. Available: {', '.join(PROVIDERS.keys())}")

        if sighting_id:
            from duck.models import DuckLocation, DuckLocationPhoto
            try:
                duck_location = DuckLocation.objects.get(pk=sighting_id)
            except DuckLocation.DoesNotExist:
                raise CommandError(f"DuckLocation {sighting_id} not found")

            photo = DuckLocationPhoto.objects.filter(duck_location=duck_location).first()
            photo_url = photo.display_thumbnail_url if photo else None

            duck = duck_location.duck
            self.stdout.write(f"Sharing: Duck #{duck.duck_id} at {duck_location.location}")
            if photo_url:
                self.stdout.write(f"Photo: {photo_url}")

            if dry_run:
                for provider in configured:
                    if platform and provider.name != platform:
                        continue
                    caption = provider._build_caption(duck_location)
                    self.stdout.write(f"\n[{provider.name}] Would post:")
                    self.stdout.write(caption)
                return

            providers_to_use = [p for p in configured if not platform or p.name == platform]
            for provider in providers_to_use:
                try:
                    result = provider.share_sighting(duck_location, photo_url)
                    self.stdout.write(self.style.SUCCESS(
                        f"[{provider.name}] Posted! ID: {result.get('post_id')}"
                    ))
                except SocialShareError as e:
                    self.stderr.write(self.style.ERROR(f"[{provider.name}] Failed: {e}"))
        else:
            # Test post with a simple message
            import requests
            from django.conf import settings

            if dry_run:
                self.stdout.write("\nWould post test message: 'Test post from Duckiehunt! 🦆'")
                return

            if platform == 'instagram' or (not platform and 'instagram' in [p.name for p in configured]):
                self.stdout.write("Skipping Instagram (requires a photo URL for testing)")

            if not platform or platform == 'facebook':
                if not settings.FB_PAGE_ID:
                    self.stderr.write(self.style.ERROR("FB_PAGE_ID not set"))
                    return

                resp = requests.post(
                    f"https://graph.facebook.com/v25.0/{settings.FB_PAGE_ID}/feed",
                    data={
                        "message": "Test post from Duckiehunt! 🦆",
                        "access_token": settings.FB_PAGE_ACCESS_TOKEN,
                    },
                    timeout=30,
                )
                data = resp.json()
                if 'error' in data:
                    self.stderr.write(self.style.ERROR(f"Facebook error: {data['error']['message']}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Facebook test post created! ID: {data.get('id')}"))
