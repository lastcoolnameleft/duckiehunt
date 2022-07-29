
## New Prod Push

```
az acr login -n duckiehunt
docker pull duckiehunt.azurecr.io/gh/duckiehunt:latest
cd duckiehunt/
docker compose down
docker compose up
```

## Admin
```
Port forward for Traefik admin
ssh -N -L 8080:localhost:8080 dh

Port forward for DH
ssh -N -L 8081:localhost:80 dh

# GH working
ssh-add -K ~/.ssh/id_rsa

docker build -t duckiehunt:latest . # Don't do with secrets
```

### Create users
```

# Dev (local)
create user dh@'%' identified by 'passwd';
grant all on duckiehunt_dev.* to dh@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;

# Azure DB for MySQL expects NO MYSQL_NAME when creating account, but does when logging in!
VM_IP=$(curl -s ifconfig.me)
MYSQL_NAME=  #this will be the hostname db
MYSQL_SERVER=
MYSQL_USER=''
MYSQL_PASSWORD=`echo $RANDOM | md5sum | head -c 20; echo`
MYSQL_DB=''
echo CREATE USER \'$MYSQL_USER\'@\'${VM_IP}\' IDENTIFIED BY \'$MYSQL_PASSWORD\'\;
echo GRANT CREATE, INSERT, UPDATE, SELECT on \`${MYSQL_DB}\`.* TO \'${MYSQL_USER}\' WITH GRANT OPTION\;
echo FLUSH PRIVILEGES\;
# Test
echo $MYSQL_PASSWORD
mysql -u $MYSQL_USER@$MYSQL_NAME -h ${MYSQL_SERVER} -p
# Cleanup
echo DROP USER \'$MYSQL_USER\'@\'${VM_IP}\'\;
```

## Update secret files
```
sudo cp ./django/duckiehunt/settings/development.py /data/duckiehunt-dev/settings/development.py
sudo cp ./django/duckiehunt/settings/staging.py /data/duckiehunt-stg/settings/staging.py
sudo cp ./django/duckiehunt/settings/production.py /data/duckiehunt-prod/settings/production.py
```