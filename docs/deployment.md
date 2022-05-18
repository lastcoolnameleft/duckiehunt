# Deployment

## Setup

### Create AKS Cluster
```shell
AKS_CLUSTER=duckiehunt-blue
ACR_NAME=duckiehunt
AKS_RG=duckiehunt
az aks create \
    --name $AKS_CLUSTER \
    --resource-group $AKS_RG \
    --dns-name-prefix $AKS_CLUSTER \
    --enable-vmss \
    --enable-managed-identity \
    --location eastus \
    --network-plugin kubenet \
    --node-count 1 \
    --node-vm-size Standard_B2s \
    --auto-upgrade-channel stable \
    --node-osdisk-type Ephemeral \

az aks get-credentials --name $AKS_CLUSTER --resource-group $AKS_RG

# Install AKS Blobfuse adapter
https://github.com/Azure/kubernetes-volume-drivers/tree/master/flexvolume/blobfuse
```

### Apply secrets

```shell
find secrets/dev -name "*.yaml" | xargs -I{} kubectl apply -f {}
find secrets/test -name "*.yaml" | xargs -I{} kubectl apply -f {}
find secrets/prod -name "*.yaml" | xargs -I{} kubectl apply -f {}

# To get all secrets from another cluster
kubectl get --no-headers secrets -n dev | awk '{print $1}' | grep -vE "(default-token|tls-secret|draft-pullsecret)" | xargs -L 1 -I{} sh -c "kubectl get secret -n dev -o yaml {} > secrets/dev/{}.yaml"
kubectl get --no-headers secrets -n test | awk '{print $1}' | grep -vE "(default-token|tls-secret|draft-pullsecret)" | xargs -L 1 -I{} sh -c "kubectl get secret -n test -o yaml {} > secrets/test/{}.yaml"
kubectl get --no-headers secrets -n prod | awk '{print $1}' | grep -vE "(default-token|tls-secret|draft-pullsecret)" | xargs -L 1 -I{} sh -c "kubectl get secret -n prod -o yaml {} > secrets/prod/{}.yaml"

# To re-create django secrets
kubectl create secret generic duckiehunt-django --from-file=secrets/dev/settings.py --from-file=secrets/dev/authfile -n dev
kubectl create secret generic duckiehunt-django --from-file=secrets/prod/settings.py --from-file=secrets/prod/authfile -n prod
```

```shell
helm install stable/nginx-ingress --namespace kube-system --name nginx-ingress

# Follow https://docs.cert-manager.io/en/latest/getting-started/install/kubernetes.html#steps
```

### Setup DB access

1. Go to Portal and add IP of LB to Client Access
2. Add MySQL users account

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
az acr login -n $ACR_NAME
draft up
```

## Prod K8S env

```shell
kubectl create ns prod
kubens prod
kubectl create secret generic duckiehunt-django --from-file=config/aks-prod-django/settings.py --from-file=config/aks-prod-django/authfile
helm install charts/duckiehunt --name duckiehunt-prod --namespace prod --values charts/duckiehunt/values-prod.yaml
```
