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
