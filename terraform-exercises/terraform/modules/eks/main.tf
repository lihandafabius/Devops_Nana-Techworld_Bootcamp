module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.24.1"

  name = "${var.environment}-${var.application_name}-eks-cluster"
  kubernetes_version = "1.36"

  subnet_ids = var.private_subnet_ids
  vpc_id = var.vpc_id

  endpoint_public_access = true

  enable_cluster_creator_admin_permissions = true

  addons = {
    coredns                = {}
    eks-pod-identity-agent = {
      before_compute = true
    }
    kube-proxy             = {}
    vpc-cni                = {
      before_compute = true
    }
    aws-ebs-csi-driver = {
      before_compute = true
      pod_identity_association = [
        {
          role_arn        = var.ebs_csi_role_arn
          service_account = "ebs-csi-controller-sa"
        }
      ]
    }

  }

  # EKS Managed Node Group(s)
  eks_managed_node_groups = {
    default = {

      ami_type       = var.ami_type
      instance_types = var.instance_types

      min_size     = 1
      max_size     = 3
      desired_size = 3
    }
  }

  fargate_profiles = {
    fargate_profile = {
      selectors = [
        {
          namespace = "java-app"
        }
      ]
    }
  }

  tags = {
    environment = var.environment
    application = var.application_name
  }


}

