data "aws_iam_policy_document" "eks_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "cluster" {
  name               = "${var.cluster_name}-cluster-role"
  assume_role_policy = data.aws_iam_policy_document.eks_assume_role.json
}

resource "aws_iam_role_policy_attachment" "cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.cluster.name
}

resource "aws_iam_role_policy_attachment" "service_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.cluster.name
}

resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.cluster.arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = var.private_endpoint
    endpoint_public_access  = var.public_endpoint
    security_group_ids      = [aws_security_group.cluster.id]
  }

  encryption_config {
    provider {
      key_arn = var.kms_key_arn
    }
    resources = ["secrets"]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  tags = var.tags
}

resource "aws_security_group" "cluster" {
  name        = "${var.cluster_name}-cluster-sg"
  description = "EKS cluster security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

data "aws_iam_policy_document" "node_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "node" {
  name               = "${var.cluster_name}-node-role"
  assume_role_policy = data.aws_iam_policy_document.node_assume_role.json
}

resource "aws_iam_role_policy_attachment" "node_worker_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.node.name
}

resource "aws_iam_role_policy_attachment" "node_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.node.name
}

resource "aws_iam_role_policy_attachment" "node_registry_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.node.name
}

resource "aws_iam_role_policy_attachment" "node_ssm_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.node.name
}

resource "aws_eks_node_group" "services" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-services"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.subnet_ids
  instance_types  = var.service_instance_types
  capacity_type   = "ON_DEMAND"

  scaling_config {
    desired_size = var.service_desired_size
    min_size     = var.service_min_size
    max_size     = var.service_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    "nodegroup-type" = "services"
  }

  tags = var.tags
}

resource "aws_eks_node_group" "workers" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-workers"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.subnet_ids
  instance_types  = var.worker_instance_types
  capacity_type   = "SPOT"

  scaling_config {
    desired_size = var.worker_desired_size
    min_size     = var.worker_min_size
    max_size     = var.worker_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    "nodegroup-type" = "workers"
  }

  taint {
    key    = "dedicated"
    value  = "workers"
    effect = "NO_SCHEDULE"
  }

  tags = var.tags
}

resource "aws_eks_node_group" "monitoring" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-monitoring"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.subnet_ids
  instance_types  = var.monitoring_instance_types
  capacity_type   = "ON_DEMAND"

  scaling_config {
    desired_size = var.monitoring_desired_size
    min_size     = var.monitoring_min_size
    max_size     = var.monitoring_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    "nodegroup-type" = "monitoring"
  }

  tags = var.tags
}

resource "aws_iam_openid_connect_provider" "main" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [var.oidc_thumbprint]
  url             = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

data "aws_iam_policy_document" "cluster_autoscaler" {
  statement {
    effect = "Allow"
    actions = [
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DescribeAutoScalingInstances",
      "autoscaling:DescribeLaunchConfigurations",
      "autoscaling:DescribeTags",
      "autoscaling:SetDesiredCapacity",
      "autoscaling:TerminateInstanceInAutoScalingGroup",
      "ec2:DescribeLaunchTemplateVersions",
      "ec2:DescribeInstanceTypes"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "cluster_autoscaler" {
  name   = "${var.cluster_name}-cluster-autoscaler"
  policy = data.aws_iam_policy_document.cluster_autoscaler.json
}

output "cluster_id" {
  value = aws_eks_cluster.main.id
}

output "cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority" {
  value = aws_eks_cluster.main.certificate_authority[0].data
}

output "cluster_name" {
  value = aws_eks_cluster.main.name
}

output "oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.main.arn
}

output "oidc_provider_url" {
  value = aws_eks_cluster.main.identity[0].oidc[0].issuer
}

output "node_role_arn" {
  value = aws_iam_role.node.arn
}

output "cluster_security_group_id" {
  value = aws_security_group.cluster.id
}

variable "cluster_name" {
  type = string
}

variable "cluster_version" {
  type    = string
  default = "1.29"
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "kms_key_arn" {
  type = string
}

variable "private_endpoint" {
  type    = bool
  default = true
}

variable "public_endpoint" {
  type    = bool
  default = false
}

variable "allowed_cidr_blocks" {
  type    = list(string)
  default = ["10.0.0.0/8"]
}

variable "oidc_thumbprint" {
  type    = string
  default = "9e99a48a9960b14926bb7f3b02e22da2b0ab7280"
}

variable "service_instance_types" {
  type    = list(string)
  default = ["m6i.large", "m6a.large"]
}

variable "service_desired_size" {
  type    = number
  default = 3
}

variable "service_min_size" {
  type    = number
  default = 3
}

variable "service_max_size" {
  type    = number
  default = 10
}

variable "worker_instance_types" {
  type    = list(string)
  default = ["c6i.large", "c6a.large"]
}

variable "worker_desired_size" {
  type    = number
  default = 5
}

variable "worker_min_size" {
  type    = number
  default = 3
}

variable "worker_max_size" {
  type    = number
  default = 20
}

variable "monitoring_instance_types" {
  type    = list(string)
  default = ["t3.medium", "t3a.medium"]
}

variable "monitoring_desired_size" {
  type    = number
  default = 2
}

variable "monitoring_min_size" {
  type    = number
  default = 2
}

variable "monitoring_max_size" {
  type    = number
  default = 5
}

variable "tags" {
  type    = map(string)
  default = {}
}
