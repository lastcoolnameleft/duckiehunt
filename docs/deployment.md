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
docker run -p 8000:8000 --name duckiehunt --rm -it -v $PWD/django:/code duckiehunt
```

## Dev K8S Env

```shell
kubectl create ns dev
kubens dev
kubectl create secret generic duckiehunt-django --from-file=config/aks-dev-django/settings.py --from-file=config/aks-dev-django/authfile
draft up
```

## Prod K8S env

```shell
kubectl create ns prod
kubens prod
kubectl create secret generic duckiehunt-django --from-file=config/aks-prod-django/settings.py --from-file=config/aks-prod-django/authfile
helm install charts/php --name duckiehunt-prod --namespace prod --values charts/php/values-prod.yaml
```