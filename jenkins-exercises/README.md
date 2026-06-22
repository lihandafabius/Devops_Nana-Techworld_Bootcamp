# ☸️ Container Orchestration with Kubernetes on AWS EKS

This project demonstrates how to migrate a traditional Docker Compose application to Kubernetes in order to achieve high availability, scalability, self-healing, and easier application management.

The original application consisted of:

* Java Spring Boot application
* MySQL database
* phpMyAdmin

Originally all services were running on a single server using Docker Compose. Any container failure required manual intervention, causing downtime for users.

To improve reliability and availability, the application was migrated to Amazon EKS (Elastic Kubernetes Service) and deployed using Kubernetes resources and Helm charts.

The project covers:

* Creating an AWS EKS cluster
* Deploying MySQL with replication using Helm
* Configuring persistent storage with EBS volumes
* Deploying a Java application with multiple replicas
* Managing configuration using ConfigMaps and Secrets
* Deploying phpMyAdmin
* Installing NGINX Ingress Controller
* Configuring Ingress routing
* Using port-forwarding for internal services
* Creating reusable Helm charts
* Packaging Kubernetes manifests for application deployment

---

## Architecture

```text
                           Internet
                               |
                               |
                    AWS Load Balancer (ELB)
                               |
                               |
                    NGINX Ingress Controller
                               |
                               |
                          Ingress Rule
                               |
                               |
                    java-mysql-app-service
                               |
              --------------------------------
              |                              |
              |                              |
      Java Application Pod          Java Application Pod
            Replica 1                     Replica 2
              |                              |
              --------------------------------
                               |
                               |
                     mysql-primary Service
                               |
                               |
                         MySQL Primary
                               |
                    -------------------
                    |                 |
                    |                 |
             MySQL Replica 1   MySQL Replica 2

```

---

<details>
<summary>Exercise 1: Create Kubernetes Cluster</summary>

<br />

An Amazon EKS cluster was created to host the application workloads.

Unlike a traditional Docker Compose deployment running on a single VM, Kubernetes provides automated scheduling, self-healing, scaling and workload distribution across multiple nodes.

### Create Cluster

The cluster was provisioned on AWS EKS.

### Verify Cluster

```bash
kubectl get nodes
```

Example:

```bash
NAME                                          STATUS   ROLES    AGE
ip-192-168-xx-xx.eu-north-1.compute.internal  Ready    <none>   2h
ip-192-168-xx-xx.eu-north-1.compute.internal  Ready    <none>   2h
```

### Key Concepts

#### Control Plane

Managed by AWS EKS and responsible for:

* API Server
* Scheduler
* Controller Manager
* etcd

#### Worker Nodes

Responsible for running application workloads.

#### Self-Healing

If a pod crashes, Kubernetes automatically recreates it.

#### Scheduling

Pods are automatically distributed across available nodes.

</details>

---

<details>
<summary>Exercise 2: Deploy MySQL with Replication</summary>

<br />

To eliminate the database as a single point of failure, MySQL was deployed using the Bitnami Helm Chart with replication enabled.

### Create StorageClass

Persistent storage was provisioned dynamically using AWS EBS CSI Driver.

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

### MySQL Helm Values

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

### Install MySQL

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install mysql bitnami/mysql \
-f mysql-values.yaml
```

### Verify Deployment

```bash
kubectl get pods
```

Example:

```bash
mysql-primary-0
mysql-secondary-0
mysql-secondary-1
```

### Key Concepts

#### StatefulSet

MySQL is deployed as a StatefulSet because:

* stable network identities
* stable storage
* ordered startup

#### Persistent Volumes

Data remains available even if pods restart.

#### Replication

Provides:

* higher availability
* read scalability
* disaster recovery

</details>

---

<details>
<summary>Exercise 3: Deploy the Java Application</summary>

<br />

The Java Spring Boot application was containerized, pushed to Docker Hub and deployed with multiple replicas.

### Build Application

```bash
./gradlew build
```

### Build Docker Image

```bash
docker build \
-t lihanda/demo-app:java-app-1.0 .
```

### Push Docker Image

```bash
docker push lihanda/demo-app:java-app-1.0
```

### Create Docker Hub Secret

The image is stored in a private Docker Hub repository.

A Kubernetes image pull secret was created:

```bash
kubectl create secret docker-registry my-registry-key \
--docker-server=https://index.docker.io/v1/ \
--docker-username=<dockerhub-user> \
--docker-password=<dockerhub-token>
```

### Create ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: mysql-config

data:
  DB_SERVER: mysql-primary
  DB_NAME: my_database
```

### Create Secret

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

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: java-mysql-app

spec:
  replicas: 2

  selector:
    matchLabels:
      app: java-mysql-app

  template:
    metadata:
      labels:
        app: java-mysql-app

    spec:
      imagePullSecrets:
      - name: my-registry-key

      containers:
      - name: java-mysql-app

        image: lihanda/demo-app:java-app-1.0

        ports:
        - containerPort: 8080
```

### Service

```yaml
apiVersion: v1
kind: Service

metadata:
  name: java-mysql-app-service

spec:
  type: ClusterIP

  selector:
    app: java-mysql-app

  ports:
  - port: 8080
    targetPort: 8080
```

### Key Concepts

#### Deployment

Responsible for:

* rolling updates
* rollback support
* pod lifecycle management

#### ReplicaSet

Ensures two application pods are always running.

#### ConfigMap

Stores non-sensitive configuration.

#### Secret

Stores sensitive values securely.

</details>

---

<details>
<summary>Exercise 4: Deploy phpMyAdmin</summary>

<br />

phpMyAdmin was deployed to provide a graphical interface for managing MySQL.

Because it is only used by administrators, a single replica was sufficient.

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: phpmyadmin-deployment

spec:
  replicas: 1

  selector:
    matchLabels:
      app: phpmyadmin

  template:
    metadata:
      labels:
        app: phpmyadmin

    spec:
      containers:
      - name: phpmyadmin

        image: phpmyadmin:latest

        ports:
        - containerPort: 80

        env:
        - name: PMA_HOST
          value: mysql-primary

        - name: PMA_PORT
          value: "3306"
```

### Service

```yaml
apiVersion: v1
kind: Service

metadata:
  name: phpmyadmin-service

spec:
  type: ClusterIP

  selector:
    app: phpmyadmin

  ports:
  - port: 80
    targetPort: 80
```

### Key Concepts

#### Service Discovery

phpMyAdmin connects to MySQL using:

```text
mysql-primary
```

which is resolved automatically by Kubernetes DNS.

#### Internal Access

The service remains internal to the cluster.

</details>

---

<details>
<summary>Exercise 5: Deploy NGINX Ingress Controller</summary>

<br />

To expose the application externally, an NGINX Ingress Controller was installed using Helm.

### Why an Ingress Controller?

Without Ingress:

* every application requires its own LoadBalancer
* higher cloud costs
* difficult routing management

With Ingress:

* one LoadBalancer
* multiple applications
* centralized routing

### Install NGINX Ingress

```bash
helm install nginx-ingress \
oci://ghcr.io/nginx/charts/nginx-ingress \
--set controller.reportIngressStatus.enabled=true \
--set controller.service.type=LoadBalancer \
--set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-scheme"="internet-facing"
```

### AWS Subnet Tagging

The ingress service initially failed to create a load balancer because the VPC subnets were tagged for an old cluster.

Error:

```text
Failed build model due to unable to resolve at least one subnet
```

### Fix

Updated subnet tags:

```text
kubernetes.io/role/elb=1
kubernetes.io/cluster/java-mysql-application=shared
```

### Verify

```bash
kubectl get svc
```

Example:

```text
nginx-ingress-controller   LoadBalancer
```

### Key Concepts

#### Ingress Controller

Runs inside the cluster and processes ingress rules.

#### Load Balancer

Provides external access to the ingress controller.

#### Internet-Facing ELB

Allows public access to the application.

</details>

---

<details>
<summary>Exercise 6: Create Ingress Rule</summary>

<br />

An Ingress resource was created to route incoming traffic to the Java application.

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress

metadata:
  name: mysql-java-app-ingress

spec:
  ingressClassName: nginx

  rules:
  - host: k8s-default-nginxing-xxxx.elb.eu-north-1.amazonaws.com

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

### Frontend Configuration

The application frontend was updated to use the ELB DNS name:

```javascript
const HOST = "k8s-default-nginxing-xxxx.elb.eu-north-1.amazonaws.com";
```

### Key Concepts

#### Ingress Rule

Defines how requests are routed.

#### Host-Based Routing

Routes traffic based on DNS hostname.

#### Backend Service

Traffic is forwarded to:

```text
java-mysql-app-service
```

which distributes requests across both replicas.

</details>

---

<details>
<summary>Exercise 7: Configure Port Forwarding for phpMyAdmin</summary>

<br />

phpMyAdmin should not be publicly accessible.

Instead, Kubernetes port forwarding was configured.

### Port Forward

```bash
kubectl port-forward svc/phpmyadmin-service 8081:80
```

### Access

```text
http://localhost:8081
```

### Benefits

* No public exposure
* Temporary access
* Better security posture

### Common Use Cases

* Databases
* Monitoring dashboards
* Internal administration tools
* Debugging applications

</details>

---

<details>
<summary>Exercise 8: Create Helm Chart for the Java Application</summary>

<br />

To improve reusability and simplify deployments, the Java application resources were packaged into a Helm Chart.

### Chart Structure

```text
java-mysql-app/
│
├── Chart.yaml
├── values.yaml
│
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    └── secret.yaml
```

### values.yaml

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

### Template Features

The chart templates support:

* configurable image tags
* configurable replicas
* configurable ingress
* configurable services
* configurable secrets
* configurable ConfigMaps

### Validate Chart

```bash
helm lint .
```

### Render Templates

```bash
helm template .
```

### Server-Side Validation

```bash
kubectl apply -f <(helm template .) --dry-run=server
```

### Install Chart

```bash
helm install java-app .
```

### Upgrade Chart

```bash
helm upgrade java-app .
```

### Restart Deployment

```bash
kubectl rollout restart deployment java-mysql-app
```

### Key Concepts

#### Helm

Package manager for Kubernetes.

#### Templates

Allow reusable Kubernetes manifests.

#### Values Files

Provide environment-specific configuration without modifying templates.

</details>

---

# Challenges & Fixes

## 1. Gradle Build Failure

### Issue

Spring Boot required a newer Gradle version than the system installation.

### Fix

Used the Gradle Wrapper:

```bash
gradle wrapper

./gradlew build
```

---

## 2. MySQL Connector Dependency Failure

### Issue

Gradle could not resolve:

```text
mysql:mysql-connector-j
```

### Fix

Updated dependency coordinates:

```groovy
implementation 'com.mysql:mysql-connector-j:9.2.0'
```

---

## 3. Docker Hub Private Repository Authentication

### Issue

Pods could not pull images from Docker Hub.

### Fix

Created image pull secret:

```bash
kubectl create secret docker-registry my-registry-key
```

and referenced it in the Deployment.

---

## 4. AWS Load Balancer Creation Failed

### Issue

Ingress service failed with:

```text
Failed build model due to unable to resolve at least one subnet
```

### Root Cause

Subnets were tagged for an old EKS cluster.

### Fix

Updated subnet tags:

```text
kubernetes.io/cluster/java-mysql-application=shared
```

---

## 5. Ingress Validation Error

### Issue

NGINX rejected ingress:

```text
spec.rules[0].host: Required value
```

### Fix

Added a valid host using the AWS ELB DNS name.

---

## 6. Application Could Read but Not Save Data

### Issue

Frontend displayed data but updates failed.

### Root Cause

Incorrect fetch URL:

```javascript
http://${HOST}update-roles
```

Missing:

```text
/
```

### Fix

```javascript
http://${HOST}/update-roles
```

---

## 7. New Docker Images Not Being Used

### Issue

After pushing a new image, the application still showed old behavior.

### Root Cause

The same image tag was reused.

### Fix

Restarted deployment:

```bash
kubectl rollout restart deployment java-mysql-app
```

or use versioned image tags.

---

## 8. Understanding Ingress vs LoadBalancer

### Initial Confusion

Both appeared to expose applications externally.

### Understanding

LoadBalancer:

```text
Internet
   |
Service
   |
Pods
```

Ingress:

```text
Internet
   |
LoadBalancer
   |
Ingress Controller
   |
Ingress Rules
   |
Services
   |
Pods
```

Ingress allows multiple applications to share a single external load balancer.

---

# Lessons Learned

* Kubernetes provides self-healing and workload orchestration.
* Stateful applications require Persistent Volumes and StatefulSets.
* Helm significantly simplifies application deployment.
* ConfigMaps and Secrets allow configuration to be externalized.
* AWS EKS networking depends heavily on correct subnet tagging.
* Ingress Controllers provide centralized routing and reduce infrastructure costs.
* Port-forwarding is useful for securely accessing internal services.
* Versioned Docker image tags are preferable to reusing the same tag.
* Helm charts make Kubernetes deployments reusable and maintainable.
* Understanding Kubernetes networking is critical when deploying production workloads.

---
