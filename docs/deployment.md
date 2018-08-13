# Deployment

## Setup

```shell
helm install stable/nginx-ingress --namespace kube-system --name nginx-ingress

helm install stable/cert-manager --set ingressShim.defaultIssuerName=letsencrypt-staging --set ingressShim.defaultIssuerKind=ClusterIssuer --name cert-manager --namespace kube-system

kubectl create secret generic blobfusecreds --from-literal accountname=duckiehunt --from-literal accountkey="$ACCOUNT_KEY" --type="azure/blobfuse"
```

## Dev Local Env

```shell
docker build . -t duckiehunt
docker run --name duckiehunt -p 80:80 --rm -v $PWD/app:/var/www/html -v $PWD/config/aks-dev:/var/www/html/application/config/development -e CI_BASE_URL=http://local.duckiehunt.com duckiehunt
```

## Dev K8S Env

```shell
kubectl create ns dev
kubens dev
kubectl create secret generic duckiehunt-file --from-file=config/aks-dev/duckiehunt.php --from-file=config/aks-dev/database.php --from-file=config/aks-dev/recaptcha.php
draft up
```

## Prod K8S env

```shell
kubectl create ns prod
kubens prod
kubectl create secret generic duckiehunt-file --from-file=config/aks-prod/duckiehunt.php --from-file=config/aks-prod/database.php --from-file=config/aks-prod/recaptcha.php
helm install charts/php --name duckiehunt-prod --namespace prod --values charts/php/values-prod.yaml
```