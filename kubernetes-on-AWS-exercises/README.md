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

> **Note:** Unlike EC2 worker nodes, where multiple pods can be scheduled onto a single instance, **each Fargate pod runs inside its own virtual machin**.v 

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

</details>

---
