data "aws_ami" "amazon_linux" {
    most_recent = true
    owners      = ["amazon"]

    filter {
        name = "name"
        values = ["al2023-ami-*-x86_64"]
    }
}

resource "aws_security_group" "app" {
    name              = "${var.project_name}-app-sg"
    description       = "Allow ssh and http access"
    vpc_id            = aws_vpc.main.id

    ingress {
        description = "SSH"
        from_port   = 22
        to_port     = 22
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        description = "HTTP (app)"
        from_port   = 5000
        to_port     = 5000
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "${var.project_name}-app-sg"
    }
}

resource "aws_instance" "app" {
    ami                    = data.aws_ami.amazon_linux.id
    instance_type          = var.instance_type
    subnet_id              = aws_subnet.public[0].id
    vpc_security_group_ids = [aws_security_group.app.id]
    key_name               = var.key_pair_name
    iam_instance_profile   = aws_iam_instance_profile.app_instance.name

    tags = {
        Name = "${var.project_name}-app-instance"
    }
}

output "app_instance_public_ip" {
    value       = aws_instance.app.public_ip
    description = "Public IP address of the EC2 instance"
}

output "ecr_repository_url" {
    value       = aws_ecr_repository.app.repository_url
    description = "URL of the ECR repository"
}