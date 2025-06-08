#!/bin/bash

MINIKUBE_PROFILE="openfaas-tp2"

minikube start --driver=docker -p $MINIKUBE_PROFILE

kubectl config use-context $MINIKUBE_PROFILE

kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

helm upgrade openfaas --install openfaas/openfaas \
    --namespace openfaas \
    --set functionNamespace=openfaas-fn \
    --set generateBasicAuth=true \
    --set nats.enabled=true

wait_for_pods() {
    local namespace=$1
    local max_wait=300
    local elapsed=0
    local check_interval=10
    
    while [ $elapsed -lt $max_wait ]; do
        pending_pods=$(kubectl get pods -n $namespace --field-selector=status.phase=Pending --no-headers 2>/dev/null | wc -l)
        
        if [ $pending_pods -eq 0 ]; then
            echo "Tous les pods dans le namespace $namespace sont sortis de l'état Pending"
            
            kubectl wait --for=condition=Ready pod --all -n $namespace --timeout=120s
            return 0
        fi
        
        echo "Il reste $pending_pods pod(s) en Pending dans $namespace. Attente..."
        sleep $check_interval
        elapsed=$((elapsed + check_interval))
    done
    
    echo "Timeout: certains pods sont encore en Pending après $max_wait secondes"
    kubectl get pods -n $namespace
    return 1
}

wait_for_pods "openfaas"

kubectl port-forward -n openfaas svc/gateway 8080:8080 &

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)

eval $(minikube docker-env -p openfaas-cluster -p $MINIKUBE_PROFILE)

faas-cli login --password $PASSWORD

faas-cli build -f stack.yml
faas-cli deploy -f stack.yml

helm install nats-connector openfaas/nats-connector \
    --namespace openfaas \
    --set nats.external.clusterName=nats \
    --set nats.external.host=nats.openfaas.svc.cluster.local \
    --set nats.external.port=4222 || echo "NATS connector déjà installé"

kubectl apply -f daily-fetcher-cronjob.yaml
