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