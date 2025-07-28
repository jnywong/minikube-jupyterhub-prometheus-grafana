# minikube-jupyterhub-prometheus-grafana

Local development environment for minikube running JupyterHub, Prometheus and Grafana. Assumes platform used is [macOS with a Docker driver](https://minikube.sigs.k8s.io/docs/drivers/docker/).

[Kubernetes on minikube (for learning and development only) — Zero to JupyterHub with Kubernetes  documentation](https://z2jh.jupyter.org/en/stable/kubernetes/minikube/step-zero-minikube.html)

## Create minikube cluster

1. Start a minikube cluster with the following command:

```bash
minikube start --driver=docker
```

You may have to update environment variables with

```bash
minikube -p minikube docker-env
```

and point your shell to use the minikube Docker daemon:

```bash
eval $(minikube -p minikube docker-env)
```

To test that the cluster is running, run:

```bash
kubectl get node
```

## Add helm chart repositories

1. Get the JupyterHub helm chart

```bash
helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
helm repo update
```

1. Get the Prometheus helm chart

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

1. Get the Grafana helm chart

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

1. Fetch chart dependencies

```bash
helm dep build ./helm-charts/<app/support>
```

1. Update any on-disk dependencies if required

```bash
helm dep up ./helm-charts/<app/support>
```

1. Install the charts and deploy

```bash
 python3 deployer.py <app/support> --namespace=<app/support>
```

When using `helm` commands, remember to include the namespace flags

```bash
helm list --all-namespaces
helm -n support uninstall test-release
```

## Configure Grafana

The default Grafana username and password is `admin`. You will be asked to change the password on first login.

### Encrypt Grafana token with sops and age

1. Temporarily save the Grafana token in a file called `grafana-token.secret.yaml`

1. Use [age](https://age-encryption.org/) to generate a key with

```bash
age-keygen -o key.secret.txt
```

1. Encrypt `grafana-token.secret.yaml` with the key

```bash
sops encrypt --age <age-public-key> grafana-token.secret.yaml > enc-grafana-token.secret.yaml
```

This can be checked into version control.

1. You can decrypt `enc-grafana-token.secret.yaml` by setting the environment variable `SOPS_AGE_KEY="<age-secret-key>"` and using the command

```bash
sops decrypt enc-grafana-token.secret.yaml
```

### Deploy Grafana dashboards

Ensure that you have set the environment variable `SOPS_AGE_KEY` to the age secret key in order to decrypt the Grafana token, or you can pass the file location of the `key.txt` file to `SOPS_AGE_KEY_FILE`.

```bash
python3 deployer.py grafana
```

The deployer script assumes that the Grafana dashboards are served at [http://localhost:3000](http://localhost:3000).

## Port forwarding

### JupyterHub proxy-public service

```bash
kubectl port-forward -n app service/proxy-public 8080:http
```

then visit [http://localhost:8080](http://localhost:8080)

### Prometheus server

```bash
kubectl port-forward -n support service/support-prometheus-server 9090:80
```

then visit [http://localhost:9090](http://localhost:9090)

### Grafana

```bash
kubectl port-forward -n support service/support-grafana 3000:80
```

then visit [http://localhost:3000](http://localhost:3000)

## Single-user server

The single user server pods will spin up in the same namespace as above

```bash
$ k -n app get pod
NAME                              READY   STATUS    RESTARTS   AGE
hub-5847b8cfdc-46mn9              1/1     Running   0          12m
jupyter-jnywong                   1/1     Running   0          105s
proxy-74f5974f66-c2wrk            1/1     Running   0          12m
user-scheduler-6c77bd4657-79dnz   1/1     Running   0          12m
user-scheduler-6c77bd4657-zjvmm   1/1     Running   0          12m
```

## Uninstall and shutdown cluster

When you are done, you can uninstall the chart and delete the minikube cluster.

```bash
helm -n support uninstall support
helm -n app uninstall app
```

```bash
minikube stop
```
