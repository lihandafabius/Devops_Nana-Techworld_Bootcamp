# ☸️ Kubernetes on AWS EKS – Deploying a Highly Available Java Application

This project demonstrates how to deploy a containerized Java application on **Amazon Elastic Kubernetes Service (Amazon EKS)** using a production-oriented Kubernetes architecture. The goal is to transform a traditional container deployment into a scalable, highly available, and automated platform capable of supporting modern cloud-native applications.

The application consists of three main components:

- Java Spring Boot application
- MySQL database
- phpMyAdmin

Instead of running all services on a single host, the application is deployed across an **Amazon EKS** cluster where each component is orchestrated by Kubernetes. Stateless workloads are scheduled on **AWS Fargate**, while stateful workloads run on managed EC2 worker nodes backed by persistent Amazon EBS storage.

Beyond simply deploying the application, this project also implements a complete Continuous Deployment (CD) workflow. Every code change automatically triggers a Jenkins pipeline that:

- Builds the Java application
- Creates a Docker image
- Pushes the image to Amazon Elastic Container Registry (Amazon ECR)
- Deploys the updated application to the Kubernetes cluster

The project also demonstrates infrastructure automation, storage provisioning, networking, workload scheduling, and autoscaling to create a more resilient and cost-efficient Kubernetes environment.

## Project Objectives

Throughout this project the following technologies and concepts are implemented:

- Provisioning an Amazon EKS cluster using **eksctl**
- Creating managed EC2 node groups and AWS Fargate profiles
- Deploying MySQL using Helm with persistent Amazon EBS volumes
- Deploying phpMyAdmin for database administration
- Deploying a Java Spring Boot application with multiple replicas
- Managing application configuration using Kubernetes ConfigMaps and Secrets
- Configuring networking and service exposure using Kubernetes Services and Ingress
- Building a Jenkins Continuous Deployment pipeline
- Migrating the container registry from Docker Hub to Amazon ECR
- Automatically deploying new application versions to Kubernetes
- Configuring Kubernetes Cluster Autoscaler for worker node scaling
- Implementing versioned application builds and container images
- Applying Kubernetes deployment best practices and production considerations

Rather than focusing solely on the final deployment, this documentation also covers the architectural decisions, implementation process, real-world troubleshooting, lessons learned, and production recommendations encountered throughout the project.

---

## Architecture


![Architecture](images/architecture.png)

---
<details>
<summary>Exercise 1: Create Amazon EKS Cluster</summary>

<br />

The Kubernetes cluster was provisioned using **eksctl**, a command-line tool that automates the creation and configuration of Amazon EKS clusters.

Rather than manually creating VPC resources, IAM roles, node groups and networking components through the AWS Console, **eksctl** provisions these resources using AWS best practices, making it the recommended tool for getting started with Amazon EKS.

An EKS cluster can be created either by:

- Executing `eksctl` CLI commands with the required parameters.
- Defining the entire cluster configuration in a **ClusterConfig YAML file**, which is the recommended approach for production environments.

Using a configuration file makes the infrastructure reproducible and easier to maintain while exposing advanced configuration options such as managed node groups, Fargate profiles, IAM settings, SSH access, networking, add-ons and Kubernetes version management.

### Managed Node Groups

The cluster uses an **Amazon EKS Managed Node Group** to run stateful workloads such as MySQL and phpMyAdmin.

Managed node groups simplify worker node administration by allowing AWS to handle provisioning, upgrades, health monitoring and node replacement. Multiple node groups can also be created to isolate different workloads, instance types or scaling requirements.

### AWS Fargate Profile

A **Fargate Profile** was configured for the `java-app` namespace.

Fargate allows Kubernetes pods to run without provisioning or managing EC2 instances. Instead of maintaining worker nodes, AWS automatically launches the compute resources required for each pod, allowing teams to focus on application deployment rather than infrastructure management.

> **Note:** Unlike EC2 worker nodes, where multiple pods can be scheduled onto a single instance, **each Fargate pod runs inside its own virtual machine**

### Fargate Limitations

Although Fargate significantly reduces operational overhead, it has several limitations:

- It is not suitable for stateful workloads that require direct access to persistent node storage, making EC2 nodes the preferred option for databases.
- DaemonSets are not currently supported because there is no underlying host that can run node-level agents.
- Fargate profiles must use **private subnets** and cannot assign public IP addresses directly. Internet connectivity therefore requires components such as NAT Gateways or VPC Endpoints.
- Pod capacity is limited by the number of available IP addresses within the associated subnets, making subnet planning important for larger deployments.

### Cluster Configuration

The cluster was provisioned using the following `eksctl` configuration:

![cluster creation](images/cluster_creation.png)

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: aws-managed-cluster
  region: eu-north-1
  version: "1.36"

iam:
  withOIDC: true

managedNodeGroups:
  - name: cluster-nodes
    instanceType: t3.small
    desiredCapacity: 3
    minSize: 2
    maxSize: 5

fargateProfiles:
  - name: java-app-profile
    selectors:
      - namespace: java-app

addons:
  - name: aws-ebs-csi-driver
    version: latest
    attachPolicyARNs:
      - arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy
```

The configuration creates:

- An Amazon EKS cluster running Kubernetes **1.36**.
- One managed node group consisting of **t3.small** EC2 instances.
- A dedicated Fargate profile for the Java application namespace.
- IAM OIDC integration for secure service account authentication.
- The Amazon EBS CSI Driver for dynamic persistent volume provisioning.

### verification

![Verify cluster](images/verify_cluster.png)

</details>

---

<details>
<summary>Exercise 2: Deploy MySQL and phpMyAdmin</summary>

<br />

The database layer was deployed on the managed EC2 worker nodes using the **Bitnami MySQL Helm Chart** configured in **replication mode**. Running MySQL with one primary instance and two replicas improves availability by ensuring database replicas remain available if the primary instance becomes unavailable.

The deployment was configured using the following Helm values file:

```yaml
architecture: replication

primary:
  persistence:
    storageClass: gp2

secondary:
  replicaCount: 2
  persistence:
    storageClass: gp2

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

### Why Helm?

Although MySQL could be deployed by manually creating Kubernetes resources, using the Bitnami Helm chart greatly simplifies the process.

The chart automatically creates and configures:

- StatefulSets
- Services
- PersistentVolumeClaims
- MySQL replication
- Database initialization

This reduces the amount of YAML that needs to be maintained while following Kubernetes best practices.

### Verification

![Deploy Mysql](images/deploy_mysql.png)

![Verify Mysql pods](images/verify_mysql_pods.png)


### Deploy phpMyAdmin

After MySQL was deployed, **phpMyAdmin** was deployed as a standard Kubernetes Deployment to provide a web-based interface for managing the database.

The application connects directly to the MySQL primary instance using the `mysql-primary` service created by the Helm chart.

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

        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 5

        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 20
          periodSeconds: 10

---
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

### Verification

![Deploy Phpmyadmin](images/phpmyadmin-verify.png)

</details>

---

<details>
<summary>Exercise 3: Deploy the Java Application</summary>

<br />

The Java Spring Boot application was deployed to the **AWS Fargate Profile** created for the `java-app` namespace. Running the application on Fargate eliminates the need to provision or manage EC2 instances for the application tier, allowing AWS to manage the underlying compute infrastructure.

### Create the Application Namespace

A dedicated namespace was created to logically isolate the application resources from the rest of the cluster.

```bash
kubectl create namespace java-app
```

### Create the Image Pull Secret

Since the application image was hosted on Docker Hub, a registry secret was created to allow Kubernetes to authenticate and pull the container image.

```bash
kubectl create secret docker-registry my-registry-key -n java-app \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=xxx \
  --docker-password=...
```

### Configure the Application

Application configuration was separated from the container image by using a ConfigMap for non-sensitive values and a Secret for database credentials.

#### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-config
  namespace: java-app
data:
  DB_SERVER: "mysql-primary.default.svc.cluster.local"
  DB_NAME: "my_database"
```

> **Note:** `mysql-primary.default.svc.cluster.local` is the Kubernetes DNS name of the MySQL Service. Kubernetes automatically resolves this name to the service's IP address, enabling reliable communication between the Java application running in the `java-app` namespace and the MySQL database in the `default` namespace.

#### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: java-app
type: Opaque
data:
  DB_PWD: xxx
  DB_USER: xxx
```

![Verify Secrets ](images/docker_pass.png)

### Deploy the Application

The application was deployed with **three replicas** to improve availability and fault tolerance. A `ClusterIP` Service was created to expose the application internally within the cluster.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: java-mysql-app
  namespace: java-app

spec:
  replicas: 3

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

        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"

          limits:
            cpu: "1"
            memory: "500Mi"

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

---
apiVersion: v1
kind: Service
metadata:
  name: java-mysql-app-service
  namespace: java-app

spec:
  type: ClusterIP

  selector:
    app: java-mysql-app

  ports:
  - port: 8080
    targetPort: 8080
```

### Resource Management

Resource requests and limits were defined to provide predictable scheduling and prevent a single container from consuming excessive cluster resources.

```yaml
resources:
  requests:
    cpu: "250m"
    memory: "256Mi"

  limits:
    cpu: "1"
    memory: "500Mi"
```

Defining **requests** allows Kubernetes to reserve the minimum resources required by the application when scheduling pods. **Limits** define the maximum amount of CPU and memory a container can consume.

Without resource requests, pods are assigned the **BestEffort** Quality of Service (QoS) class, making them the first candidates for eviction when a node experiences resource pressure. By defining requests, the application receives a **Burstable** QoS class, improving scheduling decisions and overall application stability.

For more information, see:

- Kubernetes Resource Management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- Pod Quality of Service Classes: https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/

### verification


![Deploy java-app](images/verify_java_dockerhub_app.png)


![Verify Fargate](images/fargate_pod.png)


</details>

---

<details>
<summary>Exercise 4: Automate Deployment with Jenkins</summary>

<br />

To eliminate manual deployments, the existing Jenkins server running inside an Amazon EC2 instance was configured to automatically deploy new application versions to the Amazon EKS cluster whenever changes were pushed to the repository.

The pipeline performs the following tasks:

- Builds the Java application
- Creates a versioned Docker image
- Pushes the image to Docker Hub
- Updates the Kubernetes deployment
- Commits the new application version back to the repository

### Preparing the Jenkins Environment

Since Jenkins was running inside a Docker container, the required Kubernetes tools first had to be installed.

#### Install kubectl

```bash
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl

chmod +x kubectl
mv kubectl /usr/local/bin/
```

### Authenticating Jenkins with Amazon EKS

Two authentication approaches can be used to allow Jenkins to communicate with the Kubernetes cluster.

#### Option 1: aws-iam-authenticator (Used)

The first approach uses **aws-iam-authenticator**, allowing `kubectl` to request temporary authentication tokens when communicating with the EKS API server.

```bash
curl -Lo aws-iam-authenticator \
https://github.com/kubernetes-sigs/aws-iam-authenticator/releases/download/v0.6.11/aws-iam-authenticator_0.6.11_linux_amd64

chmod +x aws-iam-authenticator
mv aws-iam-authenticator /usr/local/bin/
```

A Kubernetes configuration file was then created on the EC2 instance and copied into the Jenkins container.

```bash
docker cp config jenkins:/var/jenkins_home/.kube/
```

The kubeconfig references `aws-iam-authenticator` as an **exec plugin**, allowing Kubernetes to obtain authentication tokens whenever `kubectl` communicates with the cluster.

#### Option 2: AWS CLI

An alternative approach is to install the AWS CLI inside the Jenkins container.

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip

unzip awscliv2.zip
./aws/install
```

After installation, AWS credentials and the cluster region are configured using `aws configure`, after which the kubeconfig can be generated automatically.

Both approaches provide secure authentication to the EKS cluster. This project uses **aws-iam-authenticator**.

### Parameterizing the Kubernetes Deployment

To allow Jenkins to deploy different application versions automatically, the deployment manifest was parameterized.

For example, placeholders such as:

```yaml
metadata:
  name: $APP_NAME

image: lihanda/demo-app:$IMAGE_NAME
```

are replaced during the pipeline using environment variables, allowing the same deployment manifest to be reused across builds.

### Environment Variable Substitution

The Jenkins container was configured with **envsubst** from the `gettext-base` package.

```bash
apt-get install -y gettext-base
```

During deployment, the placeholders inside the Kubernetes manifest are automatically replaced before being applied to the cluster.

```bash
envsubst < application-deployment.yaml | kubectl apply -f -
```

> **Note:** The CI/CD pipeline applies only the application deployment manifest (which also defines the Service). Cluster resources such as the Namespace, ConfigMaps, Secrets, and Docker registry credentials are considered infrastructure components and were created during the initial environment setup. Separating infrastructure provisioning from application deployment results in a simpler, faster, and more maintainable deployment pipeline.

### Jenkins Pipeline

The pipeline automates the complete deployment workflow by:

- Incrementing the application version
- Building the Spring Boot application using Gradle
- Building and pushing a Docker image
- Deploying the updated image to Kubernetes
- Committing the version change back to GitHub

### Jenkinsfile
```groovy
#!/usr/bin/env groovy

pipeline {
    agent any

    stages {
        stage('Increment version') {
            steps {
                dir('kubernetes-on-AWS-exercises/java-app') {
                    script {

                        def props = readFile('gradle.properties')

                        def currentVersion = props
                                .split("=")[1]
                                .trim()

                        def parts = currentVersion.tokenize('.')

                        def major = parts[0].toInteger()
                        def minor = parts[1].toInteger()
                        def patch = parts[2].toInteger() + 1

                        def newVersion = "${major}.${minor}.${patch}"

                        writeFile(
                            file: 'gradle.properties',
                            text: "version=${newVersion}\n"
                        )

                        env.IMAGE_NAME = "${newVersion}-${BUILD_NUMBER}"

                        echo "Old version: ${currentVersion}"
                        echo "New version: ${newVersion}"
                    }
                }
            }
        }

        stage('build app') {
            steps {
                dir('kubernetes-on-AWS-exercises/java-app') {
                    sh 'chmod +x gradlew'
                    sh './gradlew clean build'
                }
            }
        }

        stage('build image') {
            steps {
                script {
                    echo "building the docker image..."
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', passwordVariable: 'PASS', usernameVariable: 'USER')]){
                        sh "cd kubernetes-on-AWS-exercises/java-app && docker build -t lihanda/demo-app:${IMAGE_NAME} ."
                        sh 'echo "$PASS" | docker login -u "$USER" --password-stdin'
                        sh "docker push lihanda/demo-app:${IMAGE_NAME}"
                    }
                }
            }
        }

        stage('deploy') {
            environment {
                AWS_ACCESS_KEY_ID = credentials('jenkins_aws_access_key_id')
                AWS_SECRET_ACCESS_KEY = credentials('jenkins_aws_secret_access_key')
                APP_NAME = 'java-mysql-app'
            }
            steps {
                script {
                   echo 'deploying docker image...'
                   sh 'envsubst < kubernetes-on-AWS-exercises/application-deployment.yaml | kubectl apply -f -'
                }
            }
        }
        stage('Commit version update') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        sh 'git config --global user.email "jenkins@example.com"'
                        sh 'git config --global user.name "jenkins"'

                        sh "git remote set-url origin https://${USER}:${PASS}@github.com/lihandafabius/Devops_Nana-Techworld_Bootcamp.git"
                        sh 'git add .'
                        sh 'git commit -m "ci: version bump"'
                        sh 'git push origin HEAD:main'
                    }
                }
            }
        }
    }
}

```

### Automatic Versioning

Application versions are managed using the `gradle.properties` file.

```properties
version=1.0.0
```

During every pipeline execution, the patch version is automatically incremented and combined with the Jenkins build number to generate a unique Docker image tag.
This ensures every deployment is traceable and avoids overwriting previously published container images.

### Docker Image

The application is packaged into a lightweight container using the following Dockerfile.

```dockerfile
FROM eclipse-temurin:21-jre-jammy

WORKDIR /opt/app

COPY build/libs/java-app.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

### Jenkins Credentials

Sensitive information such as Docker Hub credentials, GitHub credentials, and AWS access keys were stored securely in the Jenkins Credentials Store rather than being hardcoded into the pipeline.

The pipeline retrieves these credentials dynamically during execution, following CI/CD security best practices.

![Jenkins Credentials](images/credentials.png)

> **Note:** While the Jenkins Credentials Store is suitable for small projects and learning environments, production environments typically use dedicated secrets management solutions such as **AWS Secrets Manager** or **HashiCorp Vault**. These services provide centralized secret management, automatic credential rotation, fine-grained access control, auditing, and tighter integration with cloud-native workloads.

</details>

---
