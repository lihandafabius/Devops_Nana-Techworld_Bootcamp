module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "21.24.1"

  name = "java-app-eks-cluster"
  kubernetes_version = "1.36"

  subnet_ids = module.java_app_vpc.private_subnets
  vpc_id = module.java_app_vpc.vpc_id

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
    aws-ebs-csi-driver     = {
      before_compute = true
    }
  }

  iam_role_additional_policies = {
    AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  }

  # EKS Managed Node Group(s)
  eks_managed_node_groups = {
    dev_eks_managed_node_group = {

      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.micro"]

      min_size     = 1
      max_size     = 3
      desired_size = 3
    }
  }

  fargate_profiles = {
    dev_fargate_profile = {
      selectors = [
        {
          namespace = "java-app"
        }
      ]
    }
  }

  tags = {
    environment = "dev"
    application = "java-app"
  }


}

