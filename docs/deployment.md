# Deployment

## New VM

* Create DS2 VM in East US
  * [Add Data Disk](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/add-disk)
* [Install Docker Engine](https://docs.docker.com/engine/install/ubuntu/)
* [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=apt)
* [Add MySQL Firewall rule](https://docs.microsoft.com/en-us/azure/mysql/single-server/quickstart-create-mysql-server-database-using-azure-cli#configure-a-server-level-firewall-rule)
  * `az mysql server firewall-rule create -g duckiehunt --server duckiehunt-mysql --name $RULE_NAME --start-ip-address $MY_IP --end-ip-address $MY_IP`
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

### Create users

```shell
# Dev (local)
create user dh@'%' identified by 'passwd';
grant all on duckiehunt_dev.* to dh@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
mysql -h 127.0.0.1 -u root duckiehunt_local < tmp/duckiehunt_prod.sql
docker exec -it duckiehunt-local python manage.py migrate

create user dh_local_test@'%' identified by 'passwd';
grant all on duckiehunt_local_test.* to dh_local_test@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
mysql -h 127.0.0.1 -u root duckiehunt_local_test < tmp/duckiehunt_prod.sql
docker exec -it duckiehunt-test python manage.py migrate

# Azure DB for MySQL expects NO MYSQL_NAME when creating account, but does when logging in!
SRC_IP=$(curl -s ifconfig.me)
MYSQL_NAME=    # example: dh-m
MYSQL_SERVER=  # example: dh-m.mysql.database.azure.com
MYSQL_USER=''  # example: dh_s
MYSQL_PASSWORD=`echo $RANDOM | md5sum | head -c 20; echo`
MYSQL_DB=''    # example: dh_s
echo CREATE USER \'$MYSQL_USER\'@\'${SRC_IP}\' IDENTIFIED BY \'$MYSQL_PASSWORD\'\;
echo "GRANT CREATE, INSERT, UPDATE, SELECT on \`${MYSQL_DB}\`.* TO '${MYSQL_USER}' WITH GRANT OPTION;"
echo FLUSH PRIVILEGES\;
# Test
echo $MYSQL_PASSWORD
mysql -u $MYSQL_USER@$MYSQL_NAME -h ${MYSQL_SERVER} -p
# Cleanup
echo DROP USER \'$MYSQL_USER\'@\'${SRC_IP}\'\;
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
```
