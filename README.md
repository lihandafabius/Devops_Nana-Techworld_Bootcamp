<table>
  <tr>
    <td valign="middle">
      <h1 style="border-bottom: none; margin: 0; padding: 0; line-height: 1.2;">TechWorld with Nana DevOps Bootcamp</h1>
      <span style="font-size: 15px; color: #57606a;">Hands-on projects in cloud infrastructure, CI/CD, container orchestration, observability and automation</span>
    </td>
  </tr>
</table>

---

This repository is my portfolio from the **TechWorld with Nana DevOps Bootcamp**. It brings together the projects I built while working through the full DevOps lifecycle: packaging applications into containers, automating builds and deployments, provisioning cloud infrastructure as code, orchestrating workloads on Kubernetes, and monitoring them in production-like conditions.

## Projects

| # | Project | Summary | Key Technologies |
|---|---------|---------|------------------|
| 1 | [**Artifact Repository Manager with Nexus**](./running_and_deploying_nexus_server) | Running a Nexus server and using it to store and manage build artifacts | Nexus, Maven, Gradle |
| 2 | [**Containers with Docker**](./docker-exercises) | Containerizing applications and running multi-container setups | Docker, Docker Compose |
| 3 | [**Build Automation & CI/CD with Jenkins**](./jenkins-exercises) | Pipelines that build, test and deliver applications automatically | Jenkins, Docker |
| 4 | [**AWS Services**](./aws-exercises) | Core AWS services that underpin the cloud projects that follow | AWS, EC2, IAM, VPC |
| 5 | [**Container Orchestration with Kubernetes**](./kubernetes-exercises) | Deploying a Java and MySQL application on Kubernetes, packaged as Helm charts | Kubernetes, Helm |
| 6 | [**Kubernetes on AWS (EKS)**](./kubernetes-on-AWS-exercises) | Java and MySQL application on Amazon EKS with Fargate, autoscaling, ingress and Jenkins-driven delivery | EKS, Fargate, ECR, NGINX Ingress, Jenkins |
| 7 | [**Infrastructure as Code with Terraform**](https://github.com/lihandafabius/terraform-eks-infrastructure) | Reusable Terraform modules provisioning AWS infrastructure with remote state and a CI/CD pipeline *(separate repository)* | Terraform, S3, Jenkins |
| 8 | [**Automation with Python**](./automation_with_python_exercises) | Boto3 scripts automating AWS resource monitoring and backups, run through Jenkins | Python, Boto3, Jenkins |
| 9 | [**Configuration Management with Ansible**](./ansible-exercises) | Reusable playbooks and roles for server setup, application deployment and repository management | Ansible |
| 10 | [**Monitoring & Observability with Prometheus**](./prometheus-exercises) | Metrics, dashboards and alert routing to Slack and email for a Java and MySQL application | Prometheus, Grafana, Alertmanager |

## Technology Stack

| Area | Tools |
|------|-------|
| **Cloud** | AWS (EKS, ECR, Fargate, EC2, S3, IAM, VPC) |
| **Infrastructure as Code** | Terraform, Ansible |
| **Containers & Orchestration** | Docker, Kubernetes, Helm |
| **CI/CD** | Jenkins |
| **Artifact Management** | Nexus |
| **Monitoring & Observability** | Prometheus, Grafana, Alertmanager |
| **Scripting** | Python (Boto3), Bash |


