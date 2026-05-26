## ☁️ AWS EC2 Deployment & CI/CD Automation with Jenkins

This project demonstrates how to provision AWS infrastructure using the AWS CLI, deploy a Dockerized Node.js application on an EC2 instance, and automate the deployment process using Jenkins CI/CD pipelines.

The setup includes:

- AWS IAM user and CLI configuration
- Infrastructure provisioning using AWS CLI
- Custom VPC, subnet, and security group configuration
- EC2 instance provisioning with AWS CLI
- Docker installation and container deployment
- Docker Compose configuration
- Jenkins CI/CD automation
- Secure SSH deployment automation
- Multi-branch pipeline automation with branch-specific logic
- Automatic webhook-triggered builds

The exercises simulate a real-world DevOps workflow where infrastructure, deployment, and automation are managed programmatically and integrated into CI/CD pipelines.

---

<details>
<summary>Exercise 1: Create IAM User & Permissions </summary>
<br />

To securely interact with AWS services, a dedicated IAM user was created and configured permissions required for infrastructure provisioning and deployment tasks.

### Steps:

* Created a new IAM user using the AWS Management Console
  
![IAM User](username.png)

* Created a `devops` group

![IAM User](username.png)
  
* Added the IAM user to the `devops` group

![IAM User and Group](group_and_username.png)

* Granted only the required permissions following the **least privilege principle**
* Attached the following AWS managed policies to the `devops` group:
  * `AmazonEC2FullAccess`
  * `AmazonVPCFullAccess`

![IAM Group Policies](group_policies.png)

These permissions allowed management of:
  * EC2 instances
  * VPCs and subnets
  * Security groups
  * Networking configuration
* Enabled:
  * AWS Console access for the user 
  * Programmatic access (Access Key & Secret Key)

### Key Concepts:

* **IAM (Identity and Access Management):** Controls authentication and authorization in AWS
* **Least privilege principle:** Users should only receive permissions they require
* **Programmatic access:** Required for AWS CLI interaction

</details>

---

<details>
<summary>Exercise 2: Configure AWS CLI </summary>
<br />

To interact with AWS services from the terminal, AWS CLI was concigured using the IAM credentials fot the user created earlier.

### Steps:

* Created access keys to be used for configuring AWS CLI for our user:

![Create access keys ](create_access_keys.png)

* Configured credentials using:

```bash
aws configure
```

![Configure AWS CLI ](confirm_cli_identity.png)

* Added:
  * Access Key ID
  * Secret Access Key
  * Default region
  * Output format
    
* Verified configuration as seen above using and also from the console:

```bash
aws sts get-caller-identity
```
![Confirm user](confirm_username_login.png)

</details>

---

<details>
<summary>Exercise 3: Create VPC, Subnet & Security Group </summary>
<br />

Instead of deploying resources in the default AWS network, a dedicated Virtual Private Cloud (VPC) was created for the application infrastructure.

### Steps:

* Created a custom VPC using AWS CLI

```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
```

![Create VPC](vpc.png)

* Enabled DNS support and DNS hostnames

```bash
aws ec2 modify-vpc-attribute \
--vpc-id <vpc-id> \
--enable-dns-support "{\"Value\":true}"

aws ec2 modify-vpc-attribute \
--vpc-id <vpc-id> \
--enable-dns-hostnames "{\"Value\":true}"
```

![Enable DNS](dns.png)

These settings were required to allow resources inside the VPC to resolve domain names and to automatically assign public DNS names to EC2 instances.

* **DNS support** → Enables DNS resolution within the VPC so instances can resolve domain names to IP addresses
* **DNS hostnames** → Automatically assigns public DNS hostnames to EC2 instances with public IP addresses, making them easier to access remotely

---

* Created a subnet inside the VPC

```bash
aws ec2 create-subnet \
--vpc-id <vpc-id> \
--cidr-block 10.0.1.0/24
```

![Subnet](subnet.png)

A subnet divides the VPC network into smaller network segments where resources such as EC2 instances can be deployed.

---

* Created an Internet Gateway

```bash
aws ec2 create-internet-gateway
```

![Internet Gateway](internet_geteway.png)

An Internet Gateway allows resources inside the VPC to communicate with the internet.

---

* Attached the Internet Gateway to the VPC

```bash
aws ec2 attach-internet-gateway \
--internet-gateway-id <igw-id> \
--vpc-id <vpc-id>
```

![Attach IGW](attach_igw.png)

This connects the VPC to the public internet.

---

* Created a route table

```bash
aws ec2 create-route-table \
--vpc-id <vpc-id>
```

![Route table](route_table.png)

A route table controls how network traffic is routed within the VPC and to external networks.

---

* Added a public internet route

```bash
aws ec2 create-route \
--route-table-id <route-table-id> \
--destination-cidr-block 0.0.0.0/0 \
--gateway-id <igw-id>
```

![Add RT](internet_route.png)

The route `0.0.0.0/0` directs all outbound internet traffic through the Internet Gateway.

---

* Associated the route table with the subnet

```bash
aws ec2 associate-route-table \
--route-table-id <route-table-id> \
--subnet-id <subnet-id>
```

![Attach RT](associate_subnet_rt.png)

This made the subnet public by allowing instances inside it to access the internet.

---

* Created a security group

```bash
aws ec2 create-security-group \
--group-name aws-exercises-sg \
--description "Security group for Node app" \
--vpc-id <vpc-id>
```

![Create Security Group](sg.png)

Security groups act as virtual firewalls controlling inbound and outbound traffic for EC2 instances.

---

* Added inbound rules:
  * Port `22` → SSH access
    
  ![Allow Port 22](open_ssh.png)
  
  * port `80` → HTTP access to allow  `apt update` etc
  
  ![Allow http](open_http.png)

  * Application port (`3000`) → browser access

  ![Allow app browser access](node_port.png)


</details>

---

<details>
<summary>Exercise 4: Create EC2 Instance using AWS CLI </summary>
<br />

Once networking was configured, I provisioned an EC2 instance inside the custom VPC using AWS CLI.

### Steps:

* Created an SSH key pair

```bash
aws ec2 create-key-pair --key-name aws-server-key
```

* Launched an EC2 instance

```bash
aws ec2 run-instances \
--image-id <ami-id> \
--instance-type t2.micro \
--key-name aws-server-key \
--security-group-ids <sg-id> \
--subnet-id <subnet-id>
```

* Retrieved the public IP address

```bash
aws ec2 describe-instances
```

### Key Concepts:

* **EC2:** Virtual servers running in AWS
* **Key pairs:** Used for secure SSH authentication
* **AMI (Amazon Machine Image):** Template used to create EC2 instances

</details>

---

<details>
<summary>Exercise 5: SSH into EC2 & Install Docker </summary>
<br />

After provisioning the EC2 instance, I connected to the server remotely and installed Docker to run the application containers.

### Steps:

* Connected to the instance using SSH

```bash
ssh -i aws-server-key.pem ec2-user@<public-ip>
```

* Installed Docker

For Amazon Linux:

```bash
sudo yum update -y
sudo yum install docker -y
```

* Started and enabled Docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

* Added current user to the Docker group

```bash
sudo usermod -aG docker $USER
```

* Restarted the session to apply group changes

### Verified installation:

```bash
docker ps
```

### Key Concepts:

* **Docker daemon:** Service responsible for running containers
* **Docker socket permissions:** Required for non-root Docker access
* **Linux groups:** Used to grant Docker permissions safely

</details>

---

# 🚀 Continuous Deployment Setup

After manually deploying the application, the next goal was to automate the deployment process using Jenkins CI/CD pipelines.

The objective was:
- automatically build Docker images
- push images to Docker Hub
- deploy updated versions to EC2
- avoid manual deployment steps

---

<details>
<summary>Exercise 6: Add Docker Compose for Deployment </summary>
<br />

To simplify deployment configuration and improve maintainability, I added Docker Compose to the Node.js application.

### docker-compose.yaml

```yaml
services:
  app:
    image: ${IMAGE}
    ports:
      - "3000:3000"
```

### Steps:

* Added a `docker-compose.yaml` file
* Used environment variable substitution for dynamic image deployment
* Configured the application port mapping

### Deployment Script

```bash
#!/usr/bin/env bash

export IMAGE=$1

docker compose -f docker-compose.yaml up --detach
```

### Key Concepts:

* **Docker Compose:** Simplifies container orchestration
* **Environment variable substitution:** Allows dynamic deployment versions
* **Reusable deployment configuration:** Easier scaling and maintenance

</details>

---

<details>
<summary>Exercise 7: Add "Deploy to EC2" Stage to Jenkins Pipeline </summary>
<br />

To automate deployments, I extended the Jenkins pipeline to deploy the application directly to the EC2 instance after building the Docker image.

### Steps:

* Added a deployment stage to the Jenkinsfile
* Used SSH credentials stored securely in Jenkins
* Transferred deployment files using `scp`
* Executed deployment commands remotely using `ssh`

### Example Deployment Stage

```groovy
stage('Deploy') {
    steps {
        sshagent(['ec2-server-key']) {

            sh '''
            scp -o StrictHostKeyChecking=no \
            docker-compose.yaml \
            ec2-user@<server-ip>:/home/ec2-user
            '''

            sh '''
            ssh -o StrictHostKeyChecking=no \
            ec2-user@<server-ip> \
            bash ./server-cmds.sh ${IMAGE_NAME}
            '''
        }
    }
}
```

### Key Concepts:

* **CI/CD automation:** Eliminates manual deployment steps
* **SSH Agent Plugin:** Securely injects SSH credentials into Jenkins
* **SCP:** Secure file transfer between machines
* **Remote deployment automation:** Executes deployment commands directly on the server

</details>

---

<details>
<summary>Exercise 8: Configure EC2 Security Group for Browser Access </summary>
<br />

After deployment, the application was running successfully inside Docker containers, but external browser access was blocked by the EC2 security group.

### Steps:

* Added inbound rule for the application port using AWS CLI

```bash
aws ec2 authorize-security-group-ingress \
--group-id <sg-id> \
--protocol tcp \
--port 3000 \
--cidr 0.0.0.0/0
```

* Verified security group configuration

```bash
aws ec2 describe-security-groups
```

* Accessed the application from the browser:

```text
http://<public-ip>:3000
```

### Key Concepts:

* **Cloud firewall configuration:** Controls public access to AWS resources
* **Port exposure:** Required for external browser communication
* **Security group rules:** Define allowed inbound traffic

</details>

---

<details>
<summary>Exercise 9: Configure Multi-Branch Pipeline & Webhooks </summary>
<br />

To improve the CI/CD workflow, I configured a Jenkins multibranch pipeline with automatic webhook triggering and branch-based deployment logic.

### Objectives:

* Automatically trigger pipelines on Git events
* Deploy only from the `main/master` branch
* Run tests only for feature branches

### Branch-Based Jenkinsfile Logic

```groovy
if (env.BRANCH_NAME == "main") {

    buildDockerImage()
    deployApp()

} else {

    sh 'npm test'
}
```

### Webhook Configuration

Configured repository webhooks to trigger Jenkins automatically whenever:
* code is pushed
* pull requests are created
* branches are updated

### Key Concepts:

* **Multibranch Pipelines:** Automatically discover and build repository branches
* **Webhook automation:** Eliminates SCM polling
* **Branch-based deployment strategies:** Prevents incomplete features from reaching production
* **CI vs CD separation:** Feature branches validate code while main branch deploys

</details>

---

# ⚠️ Challenges & Fixes

### 1. Docker Permission Denied on EC2

* **Issue:** Docker commands failed with:

```text
permission denied while trying to connect to the Docker daemon socket
```

* **Cause:** Current user was not part of the Docker group

* **Fix:**

```bash
sudo usermod -aG docker $USER
```

Then:
* restarted the session
* reconnected via SSH

---

### 2. Docker Compose Command Issues

* **Issue:** Deployment script failed with:

```text
unknown shorthand flag: 'f' in -f
```

* **Cause:** Incorrect Docker Compose installation/version mismatch

* **Fix:** Installed Docker Compose correctly and used:

```bash
docker compose
```

instead of legacy:

```bash
docker-compose
```

---

### 3. Jenkins Shared Library Path Reusability

* **Issue:** Shared library functions contained hardcoded application paths

* **Fix:** Refactored shared library functions to accept reusable parameters:

```groovy
buildDockerImage(imageName, appPath)
```

This improved:
* reusability
* scalability
* maintainability across projects

---

### 4. Jenkins Infinite Build Loop

* **Issue:** Jenkins continuously retriggered builds after automated version commits

* **Cause:** Pipeline-generated commits triggered webhooks again

* **Fix:** Added commit message filtering:

```groovy
if (commitMessage.contains('[skip ci]')) {
    currentBuild.result = 'NOT_BUILT'
    return
}
```

---

### 5. Missing Jenkins Plugins

* **Issue:** Pipeline failed with:

```text
No such DSL method 'readJSON'
```

* **Cause:** Required Pipeline Utility Steps plugin was missing

* **Fix:** Installed:
* Pipeline Utility Steps Plugin

---

# 📚 Key Learnings

- **Infrastructure as Code mindset:** AWS infrastructure can be provisioned programmatically using CLI commands

- **VPC networking fundamentals:**
  - subnets
  - route tables
  - security groups
  - DNS hostnames

- **Cloud security:**
  - IAM users and permissions
  - SSH key management
  - security group firewall rules

---

- **Docker deployment automation:**
  - remote container deployment
  - Docker Compose orchestration
  - dynamic image versioning

- **Jenkins CI/CD best practices:**
  - multibranch pipelines
  - webhook automation
  - branch-based deployment logic
  - reusable shared libraries

---

- **Automation & scalability:**
  - reducing manual deployment overhead
  - improving deployment consistency
  - creating reusable pipeline components

---

- **Real-world troubleshooting:**
  - Docker socket permission issues
  - Jenkins plugin dependency problems
  - webhook-triggered pipeline loops
  - deployment automation debugging
