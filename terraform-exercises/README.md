### This project is for the Devops Bootcamp Exercise for "Infrastructure as Code with Terraform" 

#### IMPORTANT - please read the following:

##### EBS CSI Driver
Since K8s version 1.23 an additional driver is required to provision K8s storage in AWS. K8s volumes attach to cloud platform's storage - for AWS this means they attach to EBS volumes. The EBS CSI driver is responsible for handling EBS storage tasks and is not installed by default so without the installation of this driver, K8s volumes cannot be attached to storage in AWS. 

Processes on the node group nodes are responsible for creating and attaching these volumes. Because of that, we need to add a permissions policy to the node group so it can request these changes through AWS - this is defined as a managed AWS policy called: AmazonEBSCSIDriverPolicy, which we are attaching to the node groups.

So the following 2 code snippets must be added to your EKS Terraform file to make sure EBS CSI driver is activated and the node group nodes have the needed permissions:

```sh
# 1. Including the add-on as part of EKS module:

cluster_addons = {
    aws-ebs-csi-driver = {}
}

# 2. Adding associated permissions as part of node group configuration:

iam_role_additional_policies = {
    AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}
```

##### MySQL EKS Dependency

An additional dependency is also required to be defined in your MySQL Terraform configuration. Use the following to ensure that Terraform waits for the EKS cluster to be fully created before provisioning dependent resources

```sh
data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_name
  depends_on = [module.eks.cluster_name]
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
  depends_on = [module.eks.cluster_name]
}

```

**Versions:**
- Terraform: v1.6.1
- eks module: 19.20.0
- vpc module: 5.2.0
- helm provider: v2.11.0 
- aws provider: v5.26.0
- kubernetes provider: v2.23.0
- ebs csi driver: v1.25.0

**Create S3 bucket:** 
- name: "my-bucket-exercise"
- region: eu-central-1

**Set variables:**
- env_prefix = "dev"
- k8s_version = "1.28"
- cluster_name = "my-cluster"
- region = "eu-central-1"

To execute the TF script:
```
terraform init

terraform apply -var-file="dev.tfvars"
```