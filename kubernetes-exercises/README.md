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
                               |z
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

An Amazon EKS cluster was created using **EKS Auto Mode**.

Unlike a traditional Docker Compose deployment running on a single VM, Kubernetes provides automated scheduling, self-healing, scaling and workload distribution across multiple nodes.

Using EKS Auto Mode simplified cluster management because AWS automatically provisions and manages the worker nodes required to run workloads.

### Create IAM Roles

Before creating the cluster, IAM roles were configured for both the EKS control plane and worker nodes.

#### Cluster IAM Role

The cluster IAM role allows the EKS control plane to interact with AWS services on behalf

![AWS EKS Cluster](images/cluster.png)

#### Verify cluster 

![AWS EKS Cluster node](images/cluster-node.png)

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

The MySQL database is the most critical component of the application because it stores all application data. Running a single MySQL container would introduce a single point of failure, meaning that if the database became unavailable, the entire application would stop functioning.

To improve reliability and availability, MySQL was deployed using replication, ensuring that database replicas are available if the primary instance becomes unavailable.

### Create a Custom StorageClass

Before deploying MySQL, persistent storage needed to be configured.

Amazon EKS Auto Mode automatically provides a default StorageClass. However, the default class was configured to use **gp2** EBS volumes.


![AWS gp2 storageclass](images/aws-storage-class.png)


Although gp2 volumes work well, AWS recommends using **gp3** volumes for most new workloads because they provide:

* better performance
* independent scaling of storage and IOPS
* lower storage costs
* more predictable performance

To take advantage of these benefits, a custom StorageClass was created using the AWS EBS CSI Driver.

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

The StorageClass was then applied to the cluster:

```bash
kubectl apply -f storageclass.yaml
```

![AWS Storageclass](images/storage-class.png)


### Why Persistent Storage Is Important

Databases are stateful applications.

Without persistent storage:

* pod deletion would remove all database data
* node failures could cause permanent data loss
* application data would not survive restarts

Using Persistent Volumes ensures that data remains available even when database pods are recreated.

### Deploy MySQL Using Helm

Although MySQL could have been deployed manually using:

* StatefulSets
* Services
* PersistentVolumeClaims
* Secrets
* ConfigMaps

this would require creating and maintaining multiple Kubernetes resources.

To simplify deployment, the Bitnami MySQL Helm Chart was used.

The Helm chart automatically provisions:

* StatefulSets
* Services
* PersistentVolumeClaims
* replication configuration
* MySQL initialization logic

This significantly reduces the amount of YAML that must be maintained while following Kubernetes best practices.

### Configure MySQL Values

A custom values file was created to configure:

* replication architecture
* storage settings
* database credentials
* replication users
* storage classes

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

The Bitnami repository was added and MySQL was installed using the custom values file.

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm install mysql --values helm-mysql-values.yaml bitnami/mysql 
```

### Verify Deployment

![Mysql pods](images/mysql-pods.png)

### Key Concepts

#### StatefulSets

MySQL is deployed as a StatefulSet because databases require:

* stable pod identities
* stable storage
* predictable startup ordering

#### Persistent Volumes

Persistent Volumes ensure database data survives:

* pod restarts
* node replacements
* rolling upgrades

#### Replication

Replication improves:

* availability
* fault tolerance
* read scalability

while reducing the risk of a single database instance becoming a bottleneck.

</details>

---

<details>
<summary>Exercise 3: Deploy the Java Application</summary>

<br />

The Java Spring Boot application was containerized, pushed to Docker Hub and deployed with multiple replicas.

Running multiple application replicas improves availability by ensuring that the application remains accessible even if a pod or node fails.

### Build the Application

The application was packaged using the Gradle Wrapper.

```bash
./gradlew build
```

### Build Docker Image

A Docker image was created from the application source code.

```bash
docker build \
-t lihanda/demo-app:java-app-1.0 .
```

### Push Docker Image

The image was then pushed to Docker Hub so that it could be pulled by the Kubernetes cluster.

```bash
docker push lihanda/demo-app:java-app-1.0
```

![Build image](images/build_image.png)

![Dockerhub image](images/dockerhub_image.png)


### Configure Access to the Private Docker Repository

The Docker image repository was configured as private.

To allow Kubernetes to pull images from Docker Hub, an image pull secret was required.

Instead of manually creating a Secret manifest containing a base64-encoded `.dockerconfigjson` file, the secret was generated directly using the Kubernetes CLI.

This approach:

* reduces manual configuration
* avoids base64 encoding mistakes
* automatically creates the required Docker authentication format

A Docker Hub Personal Access Token was used instead of the account password.

![Dockerhub token](images/docker_secret_token.png)

Using a token is considered a security best practice because:

* tokens can be revoked independently
* credentials can be rotated easily
* account passwords are never exposed to the cluster

```bash
kubectl create secret docker-registry my-registry-key \
--docker-server=https://index.docker.io/v1/ \
--docker-username=<dockerhub-user> \
--docker-password=<dockerhub-token>
```

![Dockerhub secret](images/create_secret.png)


### Create ConfigMap

Application configuration values that are not sensitive were externalized using a ConfigMap.
The database name was gotten by:

![Database name](images/get_db_name.png)

```yaml
apiVersion: v1
kind: ConfigMap

metadata:
  name: mysql-config

data:
  DB_SERVER: mysql-primary
  DB_NAME: my_database
```

The ConfigMap stores:

* database hostname
* database name
* application configuration values

without requiring application rebuilds.

### Create Secret

Database credentials were stored separately using a Kubernetes Secret.

```yaml
apiVersion: v1
kind: Secret

metadata:
  name: mysql-secret

type: Opaque

data: 
  DB_PWD: bXlwYXNzd29yZA==
  DB_USER: bXl1c2Vy
```

Unlike the Docker registry secret, this secret was created using a YAML manifest because the application requires specific environment variables that are consumed directly by the deployment.

Using a Secret instead of a ConfigMap helps separate sensitive and non-sensitive configuration.


![Mysql Config](images/mysql_config_and_secret.png)


### Deploy the Application

The deployment was configured with:

* two replicas
* Docker Hub image authentication
* ConfigMap integration
* Secret integration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-mysql-app
  labels:
    app: java-mysql-app
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
        imagePullPolicy: Always 

        ports:
        - containerPort: 8080

        env:
        - name: DB_SERVER
          valueFrom:
            configMapKeyRef:
              name: mysql-config
              key: DB_SERVER

        - name: DB_NAME
          valueFrom:
            configMapKeyRef:
              name: mysql-config
              key: DB_NAME

        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: DB_USER

        - name: DB_PWD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: DB_PWD
```

### Create Service

A ClusterIP service was created to expose the application internally within the cluster.

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

The application is not exposed directly to the internet because external access will later be managed through an Ingress Controller.

### Key Concepts

#### Deployment

Responsible for:

* rolling updates
* rollbacks
* application lifecycle management

#### ReplicaSets

Ensures that the desired number of application pods are always running.

#### ConfigMaps

Store non-sensitive configuration separately from application code.

#### Secrets

Store sensitive values such as passwords and credentials.

#### Image Pull Secrets

Allow Kubernetes to authenticate against private container registries and pull protected images securely.

</details>


---

<details>
<summary>Exercise 4: Deploy phpMyAdmin</summary>

<br />

Although MySQL can be administered using command-line tools, managing databases through a graphical interface is often faster and more convenient.

To simplify database administration and verification during development, phpMyAdmin was deployed inside the Kubernetes cluster.

Because phpMyAdmin is only used by administrators and not by application end users, high availability was not a requirement. Therefore, a single replica was sufficient.

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

### Verify Deployment

![Phpmyadmin deployment](images/create_phpmyadmin.png)


### Key Concepts

#### Service Discovery

phpMyAdmin connects to MySQL using the Kubernetes Service name:

```text
mysql-primary
```

Kubernetes DNS automatically resolves this name to the correct database endpoint.

#### Environment Variables

The `PMA_HOST` and `PMA_PORT` environment variables tell phpMyAdmin which MySQL instance it should connect to.

#### Internal Access

The service was configured as a `ClusterIP`, making it accessible only from within the cluster.

This prevents direct internet access to the database administration interface and reduces the attack surface of the environment.

</details>


---

<details>
<summary>Exercise 5: Deploy NGINX Ingress Controller</summary>

<br />

At this stage, the application was running successfully inside the Kubernetes cluster, but it was only accessible through internal cluster networking and port-forwarding.

To provide external access, an NGINX Ingress Controller was deployed.

### Why an Ingress Controller?

An Ingress resource only defines routing rules. To actually process those rules and route traffic into the cluster, an Ingress Controller is required.

Several Ingress Controller implementations exist, including:

* NGINX Ingress Controller
* AWS Load Balancer Controller
* Traefik
* HAProxy Ingress
* Kong Ingress Controller
* Istio Ingress Gateway

For this project, the NGINX Ingress Controller was selected because it is one of the most widely adopted and cloud-agnostic solutions in the Kubernetes ecosystem.

Without an Ingress Controller, every application would require its own external LoadBalancer service which would lead to:

* increases cloud costs
* creates unnecessary infrastructure
* becomes difficult to manage as the number of applications grows

An Ingress Controller provides a centralized entry point into the cluster.

This allows a single external endpoint to route traffic to multiple services based on hostnames or URL paths.

### Gateway API

Although Ingress remains widely used today, Kubernetes networking is gradually evolving toward the Gateway API.

The Gateway API addresses several limitations of traditional Ingress by providing:

* more advanced traffic routing
* traffic splitting and canary deployments
* support for TCP and UDP traffic
* better separation between platform and application teams

Ingress remains the most commonly used solution today, while Gateway API represents the future direction of Kubernetes networking.

### Install NGINX Ingress Controller

The NGINX Ingress Controller was installed using Helm from the OCI repository.

```bash
helm install nginx-ingress oci://ghcr.io/nginx/charts/nginx-ingress \
--set controller.reportIngressStatus.enabled=true \
--set controller.service.type=LoadBalancer \ 
--set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-scheme"="internet-facing"
```
> Note: Many ingress controller Helm charts default to `LoadBalancer` when deployed in cloud environments, but explicitly setting the value makes the deployment behavior clear and predictable.
> The `controller.reportIngressStatus.enabled=true` setting allows the Ingress Controller to publish its external address back to Ingress resources, making it easier to determine the endpoint assigned by AWS.
> The `aws-load-balancer-scheme=internet-facing` annotation ensures that AWS creates a public-facing load balancer. Without this configuration, the load balancer may be created as internal-only, preventing access from the public internet.

![Ingress Controller deployment](images/deploy-ingress-controller.png)


### Verify Installation

![Verify Nginx Service](images/verify_nginx_svc.png)


A loadbalancer is also provisioned in AWS

![AWS Loadbalancer](images/loadbalancer.png)


### Key Concepts

#### Ingress Controller

A Kubernetes component responsible for processing Ingress resources and routing external traffic to internal services.

#### LoadBalancer Service

Creates an AWS Elastic Load Balancer that forwards external traffic into the cluster.

#### Internet-Facing ELB

Allows applications running inside Kubernetes to be accessible from the public internet.

#### Centralized Traffic Management

Provides a single entry point for multiple applications instead of provisioning a separate load balancer for every service.

</details>


---

<details>
<summary>Exercise 6: Create Ingress Rule</summary>

<br />

After deploying the NGINX Ingress Controller, an Ingress resource was created to define how external requests should be routed to the application running inside the cluster.

### Why an Ingress Rule?

An Ingress Controller provides the routing engine, but it does not know where requests should be sent until Ingress rules are defined.

Ingress rules specify:

* which hostname users access
* which URL paths are available
* which Kubernetes service should receive the traffic

This allows multiple applications to share the same external LoadBalancer while still being routed correctly.

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

### Traffic Flow

```text
Internet
    |
AWS Load Balancer
    |
NGINX Ingress Controller
    |
Ingress Rule
    |
java-mysql-app-service
    |
+-------------------+
|                   |
Pod 1          Pod 2
```

### Frontend Configuration

The application frontend was updated to use the ELB DNS name:

![index.html chnage](images/html_change.png)

This allows the frontend JavaScript code to communicate with the backend through the Ingress endpoint instead of using localhost.


### Verify App Access
Changes were made to the application to test statefulness

![App Access](images/app_with_edit.png)


![Database Changes](images/database_changes.png)


### Key Concepts

#### Ingress Resource

Defines routing rules for incoming traffic.

#### Host-Based Routing

Routes traffic based on the requested hostname.

Examples:

```text
orders.company.com  -> Orders Service
payments.company.com -> Payments Service
```

#### Path-Based Routing

Routes traffic based on URL paths.

Examples:

```text
/app      -> Java Application
/api      -> Backend API
/admin    -> Admin Portal
```

#### Backend Service

The backend service acts as the destination for routed traffic.

In this project, requests are forwarded to:

```text
java-mysql-app-service
```

which automatically load balances traffic across the application replicas.

</details>

---

<details>
<summary>Exercise 7: Configure Port Forwarding for phpMyAdmin</summary>

<br />

phpMyAdmin should not be publicly accessible.

Instead, Kubernetes port forwarding was configured.

Port forwarding creates a temporary tunnel between a local machine and a pod or service running inside a cluster.

### Port Forward

![Port forwarding](images/port-forward.png)

### Access

```text
http://localhost:8081
```

![Phpmyadmin Access Local](images/phpmmyadmin_localhost.png)


![Verify tables](images/verify_phpmyadmin_tables.png)


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

After successfully deploying the application manually using individual Kubernetes manifests, the final step was to package the application into a reusable Helm Chart.

Helm is the de facto package manager for Kubernetes and allows applications to be distributed, versioned and deployed in a consistent and repeatable manner.

### Why Helm?

Managing multiple Kubernetes YAML files manually becomes difficult as applications grow especially for microservice applications.

For every deployment, operators would need to maintain:

* Deployment manifests
* Services
* ConfigMaps
* Secrets
* Ingress resources

Any environment-specific change would require modifying YAML files directly.

Helm solves this problem by introducing:

* reusable templates
* centralized configuration
* versioned application releases
* simplified upgrades and rollbacks

This allows developers to deploy the same application across multiple environments simply by providing different values files.


### Creating the Chart

A new chart was created using:

```bash
helm create java-mysql-app
```

The generated templates were then customized to match the application's architecture and requirements.

### Deployment Template

The deployment template was parameterized to support:

* configurable image versions
* configurable replica counts
* configurable image pull secrets
* configurable environment variables

Example:

```yaml
replicas: {{ .Values.appReplicas }}

image: "{{ .Values.appImage }}:{{ .Values.appVersion }}"
```

Environment variables were dynamically generated using the Helm `range` function:

```yaml
{{- range .Values.containerEnvVars }}
- name: {{ .name }}
  valueFrom:
{{- if .configMapKeyRef }}
    configMapKeyRef:
      name: {{ .configMapKeyRef.name }}
      key: {{ .configMapKeyRef.key }}
{{- end }}
{{- if .secretKeyRef }}
    secretKeyRef:
      name: {{ .secretKeyRef.name }}
      key: {{ .secretKeyRef.key }}
{{- end }}
{{- end }}
```

This approach eliminates duplication and allows developers to add environment variables through configuration instead of modifying templates.

### Service Template

The service configuration was made configurable through values:

```yaml
type: {{ .Values.serviceType }}
```

This allows environments to switch between:

* ClusterIP
* NodePort
* LoadBalancer

without changing template files.

### ConfigMap Template

Application configuration values were externalized into a ConfigMap template:

```yaml
data:
  DB_SERVER: {{ .Values.dbServer | quote }}
  DB_NAME: {{ .Values.dbName | quote }}
```

### Secret Template

Sensitive values were managed through a Secret template:

```yaml
stringData:
  DB_USER: {{ .Values.dbUser | quote }}
  DB_PWD: {{ .Values.dbPassword | quote }}
```

This separates sensitive configuration from application code.

### Ingress Template

Ingress resources were fully parameterized:

```yaml
ingressClassName: {{ .Values.ingressClassName }}

host: {{ .Values.ingressHost }}
```

This enables the same chart to be deployed across different clusters using different DNS names.

### Example values.yaml

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

configMapName: mysql-config

dbServer: mysql-primary
dbName: my_database

secretName: mysql-secret

dbUser: myuser
dbPassword: mypassword

ingressName: mysql-java-app-ingress

ingressClassName: nginx

ingressHost: k8s-default-nginxing-c0f0e6c192-6ea0d96868828de6.elb.eu-north-1.amazonaws.com
```

### Chart Validation

Before deployment, the chart was validated.

#### Linting

```bash
helm lint .
```

Checks:

* template syntax
* chart structure
* common Helm errors

#### Render Templates

```bash
helm template .
```

Renders Kubernetes manifests locally without deploying them.

#### Server-Side Validation

```bash
kubectl apply -f <(helm template .) --dry-run=server
```

This validates the generated manifests against the Kubernetes API server without creating resources.

### Deploy Chart

Install the application:

```bash
helm install java-app .
```

Verify release:

```bash
helm list
```

### Upgrade Chart

When application configuration changes:

```bash
helm upgrade java-app .
```

Helm compares the current state against the new templates and applies only the required changes.


This triggers a rolling restart of the pods while maintaining application availability.

### Hosting the Helm Chart

Helm charts can be hosted in several ways:

* Git repositories
* GitHub Pages
* OCI Registries
* ChartMuseum
* ArtifactHub
* Amazon ECR OCI Registry

For this project, the chart was stored in its own Git repository:

 Repository: [java-mysql-app-helm-chart](https://github.com/lihandafabius/java-mysql-app-helm-chart)

This provides version control, collaboration and easy distribution to other developers.

### Key Concepts

#### Helm

The package manager for Kubernetes.

#### Templates

Allow Kubernetes manifests to be dynamically generated.

#### Values Files

Separate configuration from templates.

#### Releases

Helm tracks application deployments as releases, enabling upgrades and rollbacks.

#### Reusability

The same chart can be deployed repeatedly across:

* development
* testing
* staging
* production

using different values files.

</details>

---

## Challenges & Fixes

### 1. MySQL Connector Dependency Failure

#### Issue

The application failed to build because Gradle could not resolve the MySQL JDBC driver dependency.

```text
mysql:mysql-connector-j
```

#### Fix

Updated the dependency to the correct Maven coordinates:

```groovy
implementation 'com.mysql:mysql-connector-j:9.2.0'
```

---

### 2. AWS Load Balancer Creation Failed

#### Issue

The NGINX Ingress Controller service failed to provision an AWS Load Balancer.

```text
Failed build model due to unable to resolve at least one subnet
```

#### Root Cause

The VPC subnets were tagged for a previous EKS cluster, preventing AWS from selecting them for the new load balancer.

#### Fix

Updated the subnet tags to reference the current EKS cluster:

```text
kubernetes.io/cluster/java-mysql-application=shared
```

---

### 3. Ingress Controller Created an Internal Load Balancer

#### Issue

The application was not accessible from the internet even though the Ingress Controller was running successfully.

#### Root Cause

AWS provisioned an internal load balancer instead of a public-facing load balancer.

#### Fix

Configured the Ingress Controller service with the following annotation:

```yaml
service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
```

This ensured AWS created a public Elastic Load Balancer (ELB).

---

### 4. Ingress Validation Error

#### Issue

The Ingress resource was rejected by the NGINX Ingress Controller.

```text
spec.rules[0].host: Required value
```

#### Fix

Added a valid host entry using the AWS ELB DNS name generated by the Ingress Controller service.

```yaml
rules:
- host: <elb-dns-name>
```

---

