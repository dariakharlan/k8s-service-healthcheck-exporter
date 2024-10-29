from kubernetes import client, config
from prometheus_client import start_http_server, Gauge
import requests
import time
import os
import logging

logging.basicConfig(level=logging.INFO)

# Set constants
ANNOTATION_KEY = os.environ['ANNOTATION_KEY']
ANNOTATION_VALUE = os.environ['ANNOTATION_VALUE']
HEALTH_ENDPOINT = os.environ['HEALTH_ENDPOINT']
NAMESPACE = os.environ.get('NAMESPACE', 'default')
EXPORTER_PORT = os.environ.get('PORT', 9100)  # Port for the Prometheus exporter
PING_FREQUENCY_SECONDS = os.environ.get('PING_FREQUENCY', 60)
IS_LOCAL = os.environ.get('IS_LOCAL', False)

# Define a gauge metric for service health
service_health_gauge = Gauge("k8s_service_health_avg", "Health status of Kubernetes services", ["service_name", "namespace"])
services_to_check = {}

# Initialize Kubernetes API client
if IS_LOCAL:
    config.load_kube_config()  # Use this if running outside a cluster
else:
    config.load_incluster_config()  # Use this if running inside a cluster

v1 = client.CoreV1Api()


def get_annotated_services():
    """
    Retrieve all services with the specific annotation.
    """
    annotated_services = []
    services = v1.list_namespaced_service(NAMESPACE)
    for svc in services.items:
        annotations = svc.metadata.annotations or {}
        if annotations.get(ANNOTATION_KEY) == ANNOTATION_VALUE:
            annotated_services.append(svc)
    return annotated_services


def check_service_health(service):
    """
    Check the /healthz endpoint of a given service and update the metric.
    """
    try:
        url = f"http://{service.spec.cluster_ip}:{service.spec.ports[0].port}{HEALTH_ENDPOINT}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        service_health_gauge.labels(service.metadata.name, service.metadata.namespace).set(1)
    except requests.RequestException as e:
        logging.exception(e)
        service_health_gauge.labels(service.metadata.name, service.metadata.namespace).set(0)


def monitor_services():
    """
    Main monitoring loop to continuously check service health.
    """
    while True:
        annotated_services = get_annotated_services()
        for service in annotated_services:
            services_to_check[service.metadata.name] = service

        for service in services_to_check.values():
            check_service_health(service)

        # Sleep before the next check
        time.sleep(PING_FREQUENCY_SECONDS)


if __name__ == "__main__":
    # Start the Prometheus exporter HTTP server
    start_http_server(EXPORTER_PORT)
    logging.info(f"Prometheus exporter running on port {EXPORTER_PORT}")

    # Start monitoring services
    monitor_services()
