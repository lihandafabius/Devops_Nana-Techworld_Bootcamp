variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "environment" {
  description = "The environment for the EKS cluster (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "instance_types" {
  description = "List of instance types for the EKS managed node group."
  type        = list(string)
  default     = ["t3.micro"]
}

 variable "ami_type" {
  description = "The AMI type for the EKS managed node group."
  type        = string
  default     = "AL2023_x86_64_STANDARD"
}
 
 variable application_name {
  description = "The name of the application for tagging purposes."
  type        = string
  default     = "java-app"
}

variable "ebs_csi_role_arn" {
  description = "The ARN of the IAM role for the EBS CSI driver."
  type        = string
}
