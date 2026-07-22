provider "aws" {
  region = "eu-north-1"
  access_key = ""
  secret_key = ""
}
 
resource "aws_vpc" "development_vpc" {
  cidr_block = "10.0.0.0/16"
    tags = {
        Name = "development_vpc"
    }

}

resource "aws_subnet" "development_subnet1" {
  vpc_id     = aws_vpc.development_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-north-1a"
    tags = {
        Name = "development_subnet1"
    }
}

data "aws_vpc" "existing_vpc" {
    default = true
}

resource "aws_subnet" "development_subnet2" {
  vpc_id     = data.aws_vpc.existing_vpc.id
  cidr_block = "172.31.48.0/20"
  availability_zone = "eu-north-1a"
    tags = {
        Name = "development_subnet2"
    }
}