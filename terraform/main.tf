provider "aws" {
  region = "eu-north-1"
  access_key = ""
  secret_key = "
}
 
# variable "cidr_blocks" {
#   description = "CIDR blocks for the subnets"
# #   default = ["10.0.40.0/24"]
#   type = list(string)
# }

# variable "cidr_blocks" {
#   description = "CIDR block for the VPC"
# #   default = ["10.0.0.0/16"]
#   type = list(string)
# } 

variable "cidr_blocks" {
  description = "CIDR blocks for the vpc and subnets"
  type = list(object({
    cidr_block = string
    name       = string
  }))
}


variable "environment" {
  description = "development environment"
  default = "development"
}

resource "aws_vpc" "development_vpc" {
  cidr_block = var.cidr_blocks[1].cidr_block
    tags = {
        Name = var.cidr_blocks[1].name
    }

}

resource "aws_subnet" "development_subnet1" {
  vpc_id     = aws_vpc.development_vpc.id
  cidr_block = var.cidr_blocks[0].cidr_block
  availability_zone = "eu-north-1a"
    tags = {
        Name = var.cidr_blocks[0].name
    }
}

output "dev_vpc_id" {
  value = aws_vpc.development_vpc.id
}

output "dev_subnet1_id" {
  value = aws_subnet.development_subnet1.id
}