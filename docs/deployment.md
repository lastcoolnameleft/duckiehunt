# Deployment

## New VM

* Create DS2 VM in East US
  * [Add Data Disk](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/add-disk)
* [Install Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
* [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)
* Add to `/etc/fstab`

```shell
UUID=2a2c8bce-0de4-4916-b960-23482ba13920   /data   xfs   defaults,nofail   1   2
```

* Install service

```shell
sudo cp duckiehunt.service /etc/systemd/system/duckiehunt.service
sudo chmod 744 /home/thfalgou/duckiehunt/startup/duckiehunt-start.sh
sudo chmod 664 /etc/systemd/system/duckiehunt.service
sudo systemctl daemon-reload
sudo systemctl enable duckiehunt.service
systemctl status duckiehunt
```

After reboot

```shell
# https://docs.microsoft.com/en-us/azure/virtual-machines/linux/add-disk
sudo mount /dev/sda1 /data
```

## New Prod Push

```shell
az acr login -n duckiehunt
docker pull duckiehunt.azurecr.io/gh/duckiehunt:latest
docker compose --file ~/duckiehunt/docker-compose/management.yaml up -d
docker compose --file ~/duckiehunt/docker-compose/development.yaml up -d
docker compose --file ~/duckiehunt/docker-compose/staging.yaml up -d
docker compose --file ~/duckiehunt/docker-compose/production.yaml up -d

docker compose --file ~/duckiehunt/docker-compose/management.yaml down
docker compose --file ~/duckiehunt/docker-compose/development.yaml down
docker compose --file ~/duckiehunt/docker-compose/staging.yaml down
docker compose --file ~/duckiehunt/docker-compose/production.yaml down
```

## Admin

```shell
#Port forward for Traefik admin
ssh -N -L 8080:localhost:8080 dh

#Port forward for DH
ssh -N -L 8081:localhost:80 dh

# GH working
ssh-add -K ~/.ssh/id_rsa

docker build -t duckiehunt:latest . # Don't do with secrets
```

## Update secret files

```shell
sudo cp ./django/duckiehunt/settings/development.py /data/duckiehunt-dev/settings/development.py
sudo cp ./django/duckiehunt/settings/staging.py /data/duckiehunt-stg/settings/staging.py
sudo cp ./django/duckiehunt/settings/production.py /data/duckiehunt-prod/settings/production.py

sudo cp ./django/duckiehunt/settings/flickr.auth /data/duckiehunt-dev/settings/flickr.auth
sudo cp ./django/duckiehunt/settings/flickr.auth /data/duckiehunt-stg/settings/flickr.auth
sudo cp ./django/duckiehunt/settings/flickr.auth /data/duckiehunt-prod/settings/flickr.auth
```

## Cleanup logs

```
# Cleanup traefik logs
truncate -s 0 $(docker inspect --format='{{.LogPath}}' traefik)
sudo truncate -s 0 $(docker inspect --format='{{.LogPath}}' traefik) && docker restart traefik
```
