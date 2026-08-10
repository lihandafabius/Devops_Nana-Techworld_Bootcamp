variable "vpc_cidr_block" {
  type = string
}

variable "private_subnet_cidr_blocks" {
  type = list(string)
}

variable "public_subnet_cidr_blocks" {
  type = list(string)
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "application_name" {
  type    = string
  default = "java-app"
}

variable "instance_types" {
  type    = list(string)
  default = ["t3.micro"]
}

variable "ami_type" {
  type    = string
  default = "AL2023_x86_64_STANDARD"
}

