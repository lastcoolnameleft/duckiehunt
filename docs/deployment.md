# Deployment

## Setup

```
helm install stable/nginx-ingress --namespace kube-system --name nginx-ingress

helm install stable/cert-manager --set ingressShim.defaultIssuerName=letsencrypt-staging --set ingressShim.defaultIssuerKind=ClusterIssuer --name cert-manager --namespace kube-system

```

## Dev Env

```
kubectl create ns dev
kubens dev
kubectl create secret generic duckiehunt-file --from-file=config/aks-dev/duckiehunt.php --from-file=config/aks-dev/database.php --from-file=config/aks-dev/recaptcha.php
draft up
```

### Dev Env Cleanup

```
draft delete
kubectl delete namespace dev
```

## Prod env

```
kubectl create ns prod
kubens prod
kubectl create secret generic duckiehunt-file --from-file=config/aks-prod/duckiehunt.php --from-file=config/aks-prod/database.php --from-file=config/aks-prod/recaptcha.php
helm install charts/php --name duckiehunt-prod --namespace prod --values charts/php/values-prod.yaml 
```

# To investigate
Could not get cross-ns ingress working:
https://itnext.io/save-on-your-aws-bill-with-kubernetes-ingress-148214a79dcb

## Start over
```
helm install stable/nginx-ingress --namespace kube-system --name nginx-ingress

