# Photo Storage Strategy

## Current State (May 2026)

- **Primary**: Flickr API (250 photos, all with flickr_photo_id in DB)
- **Backup**: Local disk via `sync_flickr_photos` management command
- **Abstraction**: PhotoProvider layer ready for swapping providers (#101)

## Flickr Pros/Cons

**Pros:**
- Stable hosting — photos have been there for years
- Free tier is generous (1000 photos)
- Good CDN performance
- No deletion due to inactivity

**Cons:**
- Authentication is fragile (OAuth 1.0a, tokens expire)
- Flickr API library (`flickr_api`) is poorly maintained
- If auth breaks, uploads fail (reads still work via public URLs)

## Imgur Evaluation

**Pros:**
- Simple API (OAuth 2.0, easier auth flow)
- Fast CDN
- Easy to integrate

**Cons:**
- **Images deleted after ~6 months of inactivity** (no views)
- Even account-linked images at risk if they don't get views
- Active purging since May 2023 — ongoing policy
- Duckiehunt photos are niche and unlikely to get regular external views
- Would trade one fragile dependency for one with data loss risk

## Recommendation

**Stay on Flickr. Don't migrate to Imgur.**

1. Run `sync_flickr_photos` periodically to maintain local backups
2. If Flickr auth breaks, serve photos from local disk as fallback
3. Only migrate if Flickr introduces breaking changes or shuts down
4. If migrating becomes necessary, consider self-hosted options (S3, Azure Blob) over Imgur

## Alternative Options (if needed later)

| Option | Cost | Durability | Complexity |
|--------|------|-----------|------------|
| Flickr (current) | Free | High | Medium (auth) |
| Azure Blob Storage | ~$0.02/GB/mo | Very High | Low |
| AWS S3 | ~$0.023/GB/mo | Very High | Low |
| Imgur | Free | **Low (deletion risk)** | Low |
| Self-hosted (disk) | Server cost | Depends on backup | Very Low |

## References

- Imgur deletion policy: https://wiki.archiveteam.org/index.php/Imgur
- Flickr sync command: `python manage.py sync_flickr_photos`
- Provider abstraction: `django/duck/photo_providers.py`
