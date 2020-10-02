terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key
  token      = var.token
}



resource "aws_default_vpc" "vpc" {
  tags = {
    Name = "Default VPC"
  }
}

resource "aws_default_subnet" "default_az1" {
  availability_zone = "${var.region}a"
}

resource "aws_security_group" "app_security_group" {
  name   = "security-group-caas"
  vpc_id = aws_default_vpc.vpc.id

  ingress {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80

    cidr_blocks = [
      "0.0.0.0/0",
    ]
  }
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_ecs_cluster" "cluster" {
  name = "msc-caas"
}

resource "aws_ecs_task_definition" "task_def" {
  family                = "msc-caas-family"
  requires_compatibilities = ["FARGATE"]
  cpu = var.cpu
  memory = var.memory
  network_mode = "awsvpc"
  container_definitions = <<DEFINITION
[{
    "essential": true,
    "image": "viniciusbarros/msc-performance-web-app:latest",
    "name": "msc-caas",
    "portMappings": [{
        "containerPort": 80,
        "hostPort": 80
    }]
}]
DEFINITION
}


resource "aws_ecs_service" "service" {
  name          = "msc-caas"
  cluster       = aws_ecs_cluster.cluster.id
  desired_count = 1

  task_definition = aws_ecs_task_definition.task_def.arn
  launch_type = "FARGATE"
  network_configuration {
      assign_public_ip = true
      security_groups = [aws_security_group.app_security_group.id]
      subnets = [aws_default_subnet.default_az1.id]
  }
#   DAEMON not suported for FARGATE launch types :(
  scheduling_strategy = "REPLICA"

#   load_balancer {
#     target_group_arn = aws_lb_target_group.foo.arn
#     container_name   = "TO-DO"
#     container_port   = 80
#   }
}
