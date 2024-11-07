# K8S services healthcheck exporter

Discovers services by specified annotation key/value and queries a specific endpoint for each of them

Usage:
```bash
helm repo add k8s-service-healthcheck-exporter https://dariakharlan.github.io/k8s-service-healthcheck-exporter 
helm upgrade --install k8s-service-healthcheck-exporter k8s-service-healthcheck-exporter/k8s-service-healthcheck-exporter -n monitoring
```