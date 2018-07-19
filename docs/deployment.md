# Deployment


## Dev Env

```
helm del --purge dev-app  nginx-ingress dev-cert-manager
kubectl delete ns dev
```

```
kubectl create ns dev
helm install stable/nginx-ingress --namespace dev --name nginx-ingress

helm install stable/cert-manager --set ingressShim.defaultIssuerName=letsencrypt-staging --set ingressShim.defaultIssuerKind=ClusterIssuer --name dev-cert-manager --namespace=dev
#helm install stable/cert-manager --set ingressShim.defaultIssuerName=letsencrypt-prod --set ingressShim.defaultIssuerKind=ClusterIssuer --name dev-cert-manager --namespace dev

kubectl create secret generic duckiehunt-file --from-file=config/aks-dev/duckiehunt.php --from-file=config/aks-dev/database.php --from-file=config/aks-dev/recaptcha.php

helm del --purge dev-app; helm install --name dev-app --namespace dev --set ingress.enabled=true,env.ciBaseUrl=https://aks-dev.duckiehunt.com/,ingress.hostname=aks-dev.duckiehunt.com charts/php
```

# To investigate
Could not get cross-ns ingress working:
https://itnext.io/save-on-your-aws-bill-with-kubernetes-ingress-148214a79dcb
