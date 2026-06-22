#### This project is for the Devops Bootcamp Exercise for 
#### "Container Orchestration with Kubernetes" 


# Kubernetes Container Orchestration Project – Java Application with MySQL on AWS EKS

## Project Overview

This project demonstrates how a traditional Docker Compose application can be migrated to Kubernetes to achieve:

* High Availability
* Self-Healing Infrastructure
* Scalability
* Container Orchestration
* Persistent Storage
* Secure Configuration Management
* Ingress-Based Application Access
* Helm-Based Application Packaging

The original application consists of:

* Java Spring Boot application
* MySQL database
* phpMyAdmin

Initially the application was running on a single server using Docker Compose. Any container failure required manual intervention, causing downtime for internal users and customers.

To improve reliability and availability, the application was migrated to Kubernetes running on Amazon EKS.

---

# Architecture

```text
                    Internet
                        |
                        |
                AWS Load Balancer
                        |
                        |
                NGINX Ingress Controller
                        |
                -------------------
                |                 |
                |
        Java Application Service
                |
        -----------------
        |               |
        |
    Java Pod 1      Java Pod 2
                |
                |
          MySQL Service
                |
       -------------------
       |                 |
       |
   MySQL Primary    MySQL Secondary
      StatefulSet     StatefulSet
                |
          EBS Volumes
                |
          Persistent Data

```

---

# Technologies Used

* Kubernetes
* Amazon EKS
* Helm
* Docker
* Docker Hub
* MySQL
* phpMyAdmin
* AWS EBS CSI Driver
* NGINX Ingress Controller

---

# Exercise 1 – Create Kubernetes Cluster

## Goal

Create a Kubernetes cluster capable of hosting a highly available application.

## Solution

Amazon EKS was used instead of Minikube.

### Cluster Features

* Managed Control Plane
* Multiple Worker Nodes
* Public API Endpoint
* EBS CSI Driver enabled
* Public Load Balancer support

Verify cluster:

```bash
kubectl get nodes
```

Expected output:

```bash
NAME                     STATUS   ROLES
ip-xxx-xxx-xxx-xxx       Ready    <none>
ip-xxx-xxx-xxx-xxx       Ready    <none>
```

---

# Exercise 2 – Deploy MySQL with Replication

## Goal

Deploy MySQL with:

* Primary instance
* Secondary replicas
* Persistent storage

## Storage Class

Created a custom StorageClass using AWS EBS.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: auto-ebs

provisioner: ebs.csi.eks.amazonaws.com

volumeBindingMode: WaitForFirstConsumer

parameters:
  type: gp3

allowVolumeExpansion: true
```

Deploy:

```bash
kubectl apply -f storage-class.yaml
```

---

## MySQL Deployment

MySQL was deployed using the Bitnami Helm Chart.

Custom values:

```yaml
architecture: replication

primary:
  persistence:
    storageClass: auto-ebs

secondary:
  replicaCount: 2
  persistence:
    storageClass: auto-ebs

auth:
  username: myuser
  password: mypassword
  rootPassword: rootpassword
  replicationUser: replicator
  replicationPassword: replica123

global:
  security:
    allowInsecureImages: true

image:
  registry: docker.io
  repository: bitnamilegacy/mysql
  tag: latest
```

Install:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install mysql bitnami/mysql \
-f mysql-values.yaml
```

Verify:

```bash
kubectl get pods
```

---

# Exercise 3 – Deploy Java Application

## Goal

Deploy the Java application with:

* 2 replicas
* Externalized configuration
* Secure credentials

---

## Build Application

Build artifact:

```bash
./gradlew build
```

Build Docker image:

```bash
docker build -t lihanda/demo-app:java-app-1.0 .
```

Push image:

```bash
docker push lihanda/demo-app:java-app-1.0
```

---

## Docker Hub Authentication

Create image pull secret:

```bash
kubectl create secret docker-registry my-registry-key \
--docker-server=https://index.docker.io/v1/ \
--docker-username=<dockerhub-user> \
--docker-password=<dockerhub-token>
```

---

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: mysql-config

data:
  DB_SERVER: mysql-primary
  DB_NAME: my_database
```

Deploy:

```bash
kubectl apply -f configmap.yaml
```

---

## Secret

```yaml
apiVersion: v1
kind: Secret

metadata:
  name: mysql-secret

type: Opaque

stringData:
  DB_USER: myuser
  DB_PWD: mypassword
```

Deploy:

```bash
kubectl apply -f secret.yaml
```

---

## Java Deployment

Features:

* 2 replicas
* Pulls image from Docker Hub
* Reads values from ConfigMap and Secret
* Connects to MySQL primary service

Deploy:

```bash
kubectl apply -f deployment.yaml
```

---

## Java Service

```yaml
type: ClusterIP
```

The service is internal because application traffic will be routed through Ingress.

Deploy:

```bash
kubectl apply -f service.yaml
```

---

# Exercise 4 – Deploy phpMyAdmin

## Goal

Deploy phpMyAdmin for database administration.

Only one replica is required.

---

## Deployment

Environment variables:

```yaml
env:
- name: PMA_HOST
  value: mysql-primary

- name: PMA_PORT
  value: "3306"
```

Deploy:

```bash
kubectl apply -f phpmyadmin-deployment.yaml
```

---

## Service

```yaml
type: ClusterIP
```

Deploy:

```bash
kubectl apply -f phpmyadmin-service.yaml
```

---

# Exercise 5 – Deploy NGINX Ingress Controller

## Goal

Provide external access to the application using a DNS endpoint.

---

## AWS Subnet Tagging

The EKS subnets must be tagged:

```text
kubernetes.io/role/elb=1
kubernetes.io/cluster/<cluster-name>=shared
```

Example:

```text
kubernetes.io/cluster/java-mysql-application=shared
```

---

## Install NGINX Ingress Controller

Repository:

```bash
helm repo add ingress-nginx \
https://kubernetes.github.io/ingress-nginx

helm repo update
```

Install:

```bash
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --set controller.publishService.enabled=true \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-scheme"="internet-facing"
```

Verify:

```bash
kubectl get svc
```

Expected:

```bash
nginx-ingress-controller   LoadBalancer
```

---

# Exercise 6 – Create Ingress Rule

## Goal

Expose the Java application through the NGINX Ingress Controller.

---

## Ingress Resource

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress

metadata:
  name: mysql-java-app-ingress

spec:
  ingressClassName: nginx

  rules:
  - host: <aws-elb-dns>

    http:
      paths:
      - path: /
        pathType: Prefix

        backend:
          service:
            name: java-mysql-app-service
            port:
              number: 8080
```

Deploy:

```bash
kubectl apply -f ingress.yaml
```

---

## Frontend Update

The JavaScript application was updated to point to the AWS Load Balancer DNS name.

Example:

```javascript
const HOST = "k8s-default-nginxing-xxxxxxxx.elb.eu-north-1.amazonaws.com";
```

After updating:

```bash
./gradlew build

docker build -t lihanda/demo-app:java-app-1.0 .

docker push lihanda/demo-app:java-app-1.0
```

Redeploy:

```bash
kubectl rollout restart deployment java-mysql-app
```

---

# Exercise 7 – Port Forward phpMyAdmin

## Goal

Avoid exposing phpMyAdmin publicly.

---

## Port Forward

```bash
kubectl port-forward svc/phpmyadmin-service 8081:80
```

Access:

```text
http://localhost:8081
```

Benefits:

* No public exposure
* Temporary access
* Improved security

---

# Exercise 8 – Create Helm Chart

## Goal

Package the Java application into a reusable Helm chart.

---

## Chart Structure

```text
java-mysql-app/
│
├── Chart.yaml
├── values.yaml
│
└── templates
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secret.yaml
```

---

## Values File

```yaml
appName: java-mysql-app

appReplicas: 2

appImage: lihanda/demo-app
appVersion: java-app-1.0

imagePullPolicy: Always

imagePullSecrets:
  - my-registry-key

containerPort: 8080

serviceType: ClusterIP
servicePort: 8080
```

---

## Environment Variables

```yaml
containerEnvVars:
  - name: DB_SERVER
    configMapKeyRef:
      name: mysql-config
      key: DB_SERVER

  - name: DB_NAME
    configMapKeyRef:
      name: mysql-config
      key: DB_NAME

  - name: DB_USER
    secretKeyRef:
      name: mysql-secret
      key: DB_USER

  - name: DB_PWD
    secretKeyRef:
      name: mysql-secret
      key: DB_PWD
```

---

## Validate Chart

Lint:

```bash
helm lint .
```

Render templates:

```bash
helm template .
```

Validate against cluster:

```bash
kubectl apply -f <(helm template .) --dry-run=server
```

---

## Install Chart

```bash
helm install java-app .
```

Upgrade:

```bash
helm upgrade java-app .
```

Uninstall:

```bash
helm uninstall java-app
```

---

# Key Kubernetes Concepts Demonstrated

* Deployments
* StatefulSets
* Services
* ConfigMaps
* Secrets
* Persistent Volumes
* Storage Classes
* Ingress
* Ingress Controllers
* Port Forwarding
* Helm Charts
* AWS Load Balancers
* Container Image Registries
* High Availability
* Self-Healing Infrastructure

---

# Lessons Learned

* Kubernetes automatically replaces failed Pods.
* StatefulSets provide stable network identities and storage for databases.
* ConfigMaps and Secrets separate configuration from application code.
* Ingress provides HTTP/HTTPS routing to internal services.
* AWS Load Balancers can be provisioned automatically through Kubernetes Services.
* Helm simplifies application packaging and deployment.
* Port forwarding provides secure temporary access to internal services.
* Using Kubernetes significantly improves application reliability compared to a single-server Docker Compose deployment.


