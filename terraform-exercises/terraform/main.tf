terraform {
  required_version = ">= 1.0.0"
  backend "s3" {
    bucket         = "fabius-lihanda-s3-bucket"
    key            = "java-app/state.tfstate"
    region         = "eu-north-1" # region should be the same across so multiple developers can work on the same state file
    use_lockfile     = true # state to prevent concurrent modifications
  }
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes = {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
} 


data "aws_eks_cluster" "cluster" {
  name       = module.eks.cluster_name
  depends_on = [module.eks]
}

data "aws_eks_cluster_auth" "cluster" {
  name       = module.eks.cluster_name
  depends_on = [module.eks]
}



module "vpc" {
  source = "./modules/vpc"

  vpc_cidr_block             = var.vpc_cidr_block
  private_subnet_cidr_blocks = var.private_subnet_cidr_blocks
  public_subnet_cidr_blocks  = var.public_subnet_cidr_blocks
  application_name           = var.application_name
  environment                = var.environment
}

module "eks" {
  source = "./modules/eks"

  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnets
  ebs_csi_role_arn   = module.ebs_csi_pod_identity.iam_role_arn

  environment      = var.environment
  application_name = var.application_name
  instance_types   = var.instance_types
  ami_type         = var.ami_type
}

module "ebs_csi_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.5"

  name = "${var.environment}-ebs-csi"

  attach_aws_ebs_csi_policy = true
}

module "mysql" {
  source = "./modules/mysql"

  providers = {
    kubernetes = kubernetes
    helm       = helm
  }

  depends_on = [module.eks]
}

