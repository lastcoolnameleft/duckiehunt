"""
Background tasks for duck sightings, processed by Django-Q2.

Tasks are queued from views.py after a sighting is saved, so the user
gets an immediate response. Photo upload, social sharing, and email
notifications happen asynchronously.
"""
import logging
import os

from django.conf import settings

logger = logging.getLogger(__name__)


def upload_photo_and_create_record(duck_location_id, image_path, duck_id, duck_name, comments):
    """
    Upload a photo to the configured photo provider and create the photo record.

    DEPRECATED: New flow creates the photo record in views.py first, then calls
    upload_photo. Kept for backwards compatibility with queued tasks.

    Args:
        duck_location_id: PK of the DuckLocation for this photo
        image_path: Path to the saved image file on disk
        duck_id: Duck ID for the photo title
        duck_name: Duck name for the photo title
        comments: Comments/description for the photo
    """
    from .models import DuckLocation, DuckLocationPhoto

    try:
        duck_location = DuckLocation.objects.get(pk=duck_location_id)
    except DuckLocation.DoesNotExist:
        logger.error("upload_photo_and_create_record: DuckLocation %s not found", duck_location_id)
        return

    photo = DuckLocationPhoto.objects.create(
        duck_location=duck_location,
        local_path=os.path.basename(image_path),
    )
    logger.info(
        "Created fallback photo record %s for duck #%s (location=%s, local_path=%s)",
        photo.duck_location_photo_id,
        duck_id,
        duck_location_id,
        photo.local_path,
    )
    upload_photo(photo.duck_location_photo_id, image_path, duck_id, duck_name, comments)


def upload_photo(photo_id, image_path, duck_id, duck_name, comments):
    """
    Upload a photo to the configured photo provider and update the record.

    Upload runs asynchronously after the local record is created by views.py,
    so users can see the local media file immediately while provider upload
    finishes in the background.

    Args:
        photo_id: PK of the DuckLocationPhoto to update with provider URLs
        image_path: Path to the temporarily saved image file on disk
        duck_id: Duck ID for the photo title
        duck_name: Duck name for the photo title
        comments: Comments/description for the photo
    """
    from .models import DuckLocationPhoto
    from .photo_providers import get_photo_provider

    logger.info(
        "Starting photo upload task for duck #%s (photo=%s, image_path=%s)",
        duck_id,
        photo_id,
        image_path,
    )

    if not os.path.exists(image_path):
        logger.error(
            "upload_photo: image path missing for duck #%s (photo=%s, image_path=%s)",
            duck_id,
            photo_id,
            image_path,
        )
        return

    try:
        photo = DuckLocationPhoto.objects.get(pk=photo_id)
    except DuckLocationPhoto.DoesNotExist:
        logger.error("upload_photo: DuckLocationPhoto %s not found", photo_id)
        return

    title = f"Duck #{duck_id} ({duck_name})"
    provider = get_photo_provider()
    logger.info(
        "Resolved photo provider %s for duck #%s (photo=%s, local_path=%s)",
        provider.__class__.__name__,
        duck_id,
        photo_id,
        photo.local_path,
    )

    try:
        result = provider.upload_from_path(image_path, title, comments, tags='duckiehunt')
        photo.photo_provider = provider.__class__.__name__
        photo.photo_id = str(result['id'])
        photo.thumbnail_url = result['thumbnail_url']
        photo.flickr_photo_id = result['id']
        photo.flickr_thumbnail_url = result['thumbnail_url']
        photo.save(update_fields=[
            'photo_provider',
            'photo_id',
            'thumbnail_url',
            'flickr_photo_id',
            'flickr_thumbnail_url',
        ])
        logger.info(
            "Photo uploaded for duck #%s (photo=%s, provider_id=%s, thumbnail_url=%s)",
            duck_id,
            photo_id,
            photo.photo_id,
            photo.thumbnail_url,
        )
    except Exception:
        logger.exception(
            "Photo upload failed for duck #%s (photo=%s, image_path=%s, local_path=%s)",
            duck_id,
            photo_id,
            image_path,
            photo.local_path,
        )



def share_to_social(duck_location_id):
    """
    Share a sighting to all configured social media platforms.

    Args:
        duck_location_id: PK of the DuckLocation to share
    """
    from .models import DuckLocation
    from .social import share_to_all

    try:
        duck_location = DuckLocation.objects.get(pk=duck_location_id)
    except DuckLocation.DoesNotExist:
        logger.error("share_to_social: DuckLocation %s not found", duck_location_id)
        return

    logger.info(
        "Starting social share for duck #%s (location=%s, approved=%s)",
        duck_location.duck_id,
        duck_location_id,
        duck_location.approved,
    )

    if duck_location.approved != 'Y':
        logger.info("Skipping social share for unapproved sighting %s", duck_location_id)
        return

    # Get photo URL if available
    photo_url = None
    photo = duck_location.ducklocationphoto_set.first()
    if photo and photo.flickr_thumbnail_url:
        photo_url = photo.flickr_thumbnail_url
    logger.info(
        "Social share payload for duck #%s (location=%s, photo_url_present=%s)",
        duck_location.duck_id,
        duck_location_id,
        bool(photo_url),
    )

    results = share_to_all(duck_location, photo_url=photo_url)
    for platform, result in results.items():
        if result.get('success'):
            logger.info("Shared duck #%s to %s (post: %s)",
                        duck_location.duck_id, platform, result.get('post_id'))
        else:
            logger.error("Failed to share duck #%s to %s: %s",
                         duck_location.duck_id, platform, result.get('error'))


def send_email_notification(duck_id, duck_location_url):
    """
    Send email notification about a new sighting.

    Args:
        duck_id: Duck ID for the email subject
        duck_location_url: Relative URL to the new sighting page
    """
    from django.core.mail import EmailMessage

    try:
        logger.info(
            "Preparing email notification for duck #%s (to_count=%s, backend=%s)",
            duck_id,
            len(settings.EMAIL_TO),
            settings.EMAIL_BACKEND,
        )
        msg = EmailMessage(
            f'Duckiehunt Update: Duck #{duck_id}',
            f'Duck #{duck_id} has moved!<br/>{settings.BASE_URL}{duck_location_url}',
            settings.EMAIL_FROM,
            settings.EMAIL_TO,
        )
        msg.content_subtype = "html"
        msg.send()
        logger.info("Email sent for duck #%s", duck_id)
    except Exception:
        logger.exception("Email notification failed for duck #%s", duck_id)
