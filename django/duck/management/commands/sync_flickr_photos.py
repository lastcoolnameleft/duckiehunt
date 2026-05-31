"""Download all photos from Flickr and store them locally.

For each DuckLocationPhoto with a flickr_photo_id, downloads the original
(or largest available) image from Flickr and saves it to UPLOAD_PATH.
Updates the local_path field so the container can serve or back up the file.

Usage:
    python manage.py sync_flickr_photos
    python manage.py sync_flickr_photos --size "Original"
    python manage.py sync_flickr_photos --dry-run
"""
import os
import urllib.request

import flickr_api
from django.conf import settings
from django.core.management.base import BaseCommand

from duck.models import DuckLocationPhoto


# Flickr size labels in descending preference
SIZE_PREFERENCE = [
    'Original',
    'Large',
    'Medium 800',
    'Medium',
    'Small 320',
]


class Command(BaseCommand):
    help = 'Download photos from Flickr and save locally, updating local_path on each record.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be downloaded without actually downloading.',
        )
        parser.add_argument(
            '--size', type=str, default=None,
            help=f'Preferred Flickr size label. Default: tries {SIZE_PREFERENCE}',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Re-download even if local_path is already set and file exists.',
        )
        parser.add_argument(
            '--upload-path', type=str, default=None,
            help='Override UPLOAD_PATH for downloads. Default: settings.UPLOAD_PATH',
        )

    def handle(self, *args, **options):
        upload_path = options['upload_path'] or getattr(settings, 'UPLOAD_PATH', 'uploads')
        dry_run = options['dry_run']
        force = options['force']
        preferred_size = options['size']

        os.makedirs(upload_path, exist_ok=True)
        abs_upload_path = os.path.abspath(upload_path)

        photos = DuckLocationPhoto.objects.exclude(flickr_photo_id=None)
        total = photos.count()
        self.stdout.write(f'Found {total} photos with Flickr IDs.')
        self.stdout.write(f'Download directory: {abs_upload_path}')
        self.stdout.write(f'Existing files in directory: {len(os.listdir(abs_upload_path))}')
        self.stdout.write('')

        downloaded = 0
        skipped = 0
        already_exists = 0
        failed = 0

        for photo_record in photos.iterator():
            # Skip if local_path already set and file exists (unless --force)
            if not force and photo_record.local_path:
                full_path = os.path.join(abs_upload_path, photo_record.local_path)
                if os.path.exists(full_path):
                    skipped += 1
                    continue

            flickr_id = photo_record.flickr_photo_id
            filename = f'{flickr_id}.jpg'
            dest_path = os.path.join(abs_upload_path, filename)

            # Never overwrite an existing file (unless --force)
            if not force and os.path.exists(dest_path):
                self.stdout.write(
                    f'  EXISTS flickr:{flickr_id} — {dest_path} already on disk, '
                    f'updating local_path only'
                )
                photo_record.local_path = filename
                photo_record.save(update_fields=['local_path'])
                already_exists += 1
                continue

            if dry_run:
                self.stdout.write(
                    f'  [DRY RUN] Would download flickr:{flickr_id} → {dest_path}'
                )
                downloaded += 1
                continue

            try:
                url = self._get_download_url(flickr_id, preferred_size)
                if not url:
                    self.stderr.write(f'  SKIP flickr:{flickr_id} — no sizes available')
                    failed += 1
                    continue

                self.stdout.write(f'  Downloading flickr:{flickr_id} → {dest_path}')
                urllib.request.urlretrieve(url, dest_path)

                # Update the record with relative path
                photo_record.local_path = filename
                photo_record.save(update_fields=['local_path'])
                downloaded += 1

            except Exception as e:
                self.stderr.write(f'  FAILED flickr:{flickr_id} — {e}')
                failed += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done. Downloaded: {downloaded}, Already on disk: {already_exists}, '
            f'Skipped (in DB): {skipped}, Failed: {failed}'
        ))

    def _get_download_url(self, flickr_id, preferred_size=None):
        """Get the best available download URL for a Flickr photo."""
        photo = flickr_api.Photo(id=flickr_id)
        sizes = photo.getSizes()

        if preferred_size and preferred_size in sizes:
            return sizes[preferred_size]['source']

        for size_label in SIZE_PREFERENCE:
            if size_label in sizes:
                return sizes[size_label]['source']

        # Fall back to any available size
        if sizes:
            return next(iter(sizes.values()))['source']

        return None
