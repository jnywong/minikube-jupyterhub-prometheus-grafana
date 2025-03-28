# local-dev

Local development environment for minikube running JupyterHub.

[Kubernetes on minikube (for learning and development only) — Zero to JupyterHub with Kubernetes  documentation](https://z2jh.jupyter.org/en/stable/kubernetes/minikube/step-zero-minikube.html)

## Create minikube cluster

1. Check minikube context

```bash
kubectl config current-context
```

```bash
minikube start \
--kubernetes-version stable \
--nodes 2 \
--cpus 2 \
--memory 2000 \
--cni calico
```

To test that the cluster is running, run:

```bash
kubectl get node
```

## Configure helm chart

`config.yaml` is the chart configuration file used to override the default values in the helm charts.

## Install JupyterHub

1. Get the latest chart

```bash
helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
helm repo update
```

1. Install the chart with values from `config.yaml`

```bash
helm upgrade --cleanup-on-fail \
  --install test-release jupyterhub/jupyterhub \
  --namespace support \
  --create-namespace \
  --values config.yaml
```

When using `helm` commands, remember to include the namespace flags

```bash
helm list --all-namespaces
helm -n support uninstall test-release
```

## Port forward to k8s Service proxy-public

```bash
kubectl port-forward -n support service/proxy-public 8080:http
```

then visit [http://localhost:8080](http://localhost:8080)

## Single-user server

The single user server pods will spin up in the same namespace as above

```bash
$ k -n support get pod
NAME                              READY   STATUS    RESTARTS   AGE
continuous-image-puller-29snx     1/1     Running   0          12m
hub-5847b8cfdc-46mn9              1/1     Running   0          12m
jupyter-jnywong                   1/1     Running   0          105s
proxy-74f5974f66-c2wrk            1/1     Running   0          12m
user-scheduler-6c77bd4657-79dnz   1/1     Running   0          12m
user-scheduler-6c77bd4657-zjvmm   1/1     Running   0          12m
```
