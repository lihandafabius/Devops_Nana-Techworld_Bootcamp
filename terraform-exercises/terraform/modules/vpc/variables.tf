variable vpc_cidr_block {
    type = string
}
variable private_subnet_cidr_blocks {
    type = list(string)
}
variable public_subnet_cidr_blocks {
    type = list(string)
}

variable application_name {
  description = "The name of the application for tagging purposes."
  type        = string
  default     = "java-app"
}

variable environment {
  description = "The environment for the EKS cluster (e.g., dev, staging, prod)."
  type        = string
  default     = "dev"
}