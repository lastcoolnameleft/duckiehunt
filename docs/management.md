# Traefik

```shell
docker compose -f docker-compose/management.yaml up -d
docker compose -f docker-compose/management.yaml down
```

```shell
Port forward for Traefik admin
ssh -N -L 8080:localhost:8080 dh

Port forward for Traefik admin
ssh -N -L 81:localhost:81 dh

# View dashboard
ssh -N -L 3000:localhost:3000 dh
ssh -N -L 9090:localhost:9090 dh
open http://localhost:3000/
```

# Logs

NOTE: Not implemented yet as I'm trying the build-in log rotation
```shell
vi /etc/logrotate.d/traefik


/data/traefik/*.log {
  size 10M
  rotate 5
  missingok
  notifempty
  postrotate
    docker kill --signal="USR1" traefik
  endscript
}

```

# Backup

## Database

https://litestream.io/

```yaml
dbs:
 - path: /data/duckiehunt-prod/db/duckiehunt.db
   replicas:
     - path: /data/duckiehunt-prod/db/backup
 - path: /data/capeetal-tracker-prod/db/us.db
   replicas:
     - path: /data/capeetal-tracker-prod/db/backup
```

## Photo Backup

Photos are stored locally first (for immediate in-app display at `/media/...`) and then
uploaded to Flickr asynchronously. Local disk remains the fallback/backup source.
The `sync_flickr_photos` management command downloads all photos from Flickr to the
local `UPLOAD_PATH` directory and records the file path in the database.

### Sync photos from Flickr to local disk

```bash
cd django

# Preview what will be downloaded (no changes made)
python manage.py sync_flickr_photos --dry-run

# Download all photos (skips already-downloaded files)
python manage.py sync_flickr_photos

# Force re-download everything
python manage.py sync_flickr_photos --force

# Download a specific size (Original, Large, Medium 800, Medium, Small 320)
python manage.py sync_flickr_photos --size "Original"

# Override the download destination
python manage.py sync_flickr_photos --upload-path /data/duckiehunt/prod/uploads
```

### How it works

1. Queries all `DuckLocationPhoto` records with a `flickr_photo_id`
2. For each photo, fetches the best available size from Flickr API
3. Saves the file as `{flickr_id}.jpg` in `UPLOAD_PATH`
4. Updates `DuckLocationPhoto.local_path` with the relative filename

### Correlation

Each `DuckLocationPhoto` record now tracks:
- `flickr_photo_id` / `flickr_thumbnail_url` — Flickr hosting (serving layer)
- `local_path` — relative path within `UPLOAD_PATH` (local backup)

To find the local file for a photo:
```
{UPLOAD_PATH}/{local_path}
```

On the VM: `/data/duckiehunt/prod/uploads/{local_path}`

### Recommended schedule

Run after initial setup, then periodically (e.g., weekly cron) to catch new uploads:

```bash
# Crontab entry (runs Sunday at 3am)
0 3 * * 0 cd /data/duckiehunt/prod && docker exec duckiehunt-prod python manage.py sync_flickr_photos >> /var/log/duckiehunt-photo-sync.log 2>&1
```