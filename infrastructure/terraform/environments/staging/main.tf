terraform {
  backend "s3" {
    bucket         = "schoolrail-terraform-state-staging"
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "schoolrail-terraform-locks-staging"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

locals {
  environment = "staging"
  region      = "us-east-1"

  common_tags = {
    Environment = local.environment
    Project     = "schoolrail"
    ManagedBy   = "terraform"
  }
}

module "eks" {
  source = "../../modules/eks"

  cluster_name    = "schoolrail-${local.environment}"
  cluster_version = "1.29"
  vpc_id          = data.aws_vpc.main.id
  subnet_ids      = data.aws_subnets.private.ids
  kms_key_arn     = data.aws_kms_key.eks.arn

  private_endpoint = true
  public_endpoint  = true

  service_instance_types  = ["t3.medium", "t3a.medium"]
  worker_instance_types   = ["t3.large", "t3a.large"]
  monitoring_instance_types = ["t3.small"]

  service_desired_size  = 2
  service_min_size      = 2
  service_max_size      = 5
  worker_desired_size   = 2
  worker_min_size       = 1
  worker_max_size       = 8
  monitoring_desired_size = 1
  monitoring_min_size     = 1
  monitoring_max_size     = 2

  tags = local.common_tags
}

module "rds" {
  source = "../../modules/rds"

  identifier       = "schoolrail-${local.environment}"
  vpc_id           = data.aws_vpc.main.id
  subnet_ids       = data.aws_subnets.database.ids
  allowed_security_groups = [module.eks.cluster_security_group_id]

  instance_class           = "db.t3.large"
  read_replica_instance_class = "db.t3.large"
  read_replica_count       = 1
  allocated_storage        = 100
  max_allocated_storage    = 500
  database_name            = "schoolrail"
  master_username          = "schoolrail_admin"
  master_password          = data.aws_secretsmanager_secret_version.rds_master_password.secret_string
  multi_az                 = false

  tags = local.common_tags
}

module "redis" {
  source = "../../modules/redis"

  identifier       = "schoolrail-${local.environment}"
  vpc_id           = data.aws_vpc.main.id
  subnet_ids       = data.aws_subnets.private.ids
  allowed_security_groups = [module.eks.cluster_security_group_id]

  node_type               = "cache.t3.medium"
  num_shards              = 1
  replicas_per_shard      = 1
  multi_az_enabled        = false
  snapshot_retention_days = 3

  tags = local.common_tags
}

module "rabbitmq" {
  source = "../../modules/rabbitmq"

  identifier       = "schoolrail-${local.environment}"
  vpc_id           = data.aws_vpc.main.id
  subnet_ids       = data.aws_subnets.private.ids
  allowed_security_groups = [module.eks.cluster_security_group_id]

  deployment_type = "eks"
  admin_password  = data.aws_secretsmanager_secret_version.rabbitmq_admin_password.secret_string
  multi_az        = false
  min_replicas    = 1
  max_replicas    = 3
  resources_requests_memory = "256Mi"
  resources_limits_memory   = "1Gi"

  tags = local.common_tags
}

module "vault" {
  source = "../../modules/vault"

  identifier        = "schoolrail-${local.environment}"
  namespace         = "vault"
  service_account_name = "vault"
  aws_region        = local.region
  oidc_provider_arn = module.eks.oidc_provider_arn
  oidc_provider_url = module.eks.oidc_provider_url

  vault_version       = "1.17.2"
  replicas            = 1
  injector_replicas   = 1
  resources_requests_memory = "256Mi"
  resources_requests_cpu    = "100m"
  resources_limits_memory   = "1Gi"
  resources_limits_cpu      = "500m"
  data_storage_size    = "20Gi"
  tls_cert             = data.aws_secretsmanager_secret_version.vault_tls_cert.secret_string
  tls_key              = data.aws_secretsmanager_secret_version.vault_tls_key.secret_string

  tags = local.common_tags
}

data "aws_vpc" "main" {
  tags = {
    Name = "schoolrail-${local.environment}-vpc"
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  tags = {
    Tier = "private"
  }
}

data "aws_subnets" "database" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.main.id]
  }
  tags = {
    Tier = "database"
  }
}

data "aws_kms_key" "eks" {
  key_id = "alias/eks-${local.environment}"
}

data "aws_secretsmanager_secret_version" "rds_master_password" {
  secret_id = "schoolrail/${local.environment}/rds/master-password"
}

data "aws_secretsmanager_secret_version" "rabbitmq_admin_password" {
  secret_id = "schoolrail/${local.environment}/rabbitmq/admin-password"
}

data "aws_secretsmanager_secret_version" "vault_tls_cert" {
  secret_id = "schoolrail/${local.environment}/vault/tls-cert"
}

data "aws_secretsmanager_secret_version" "vault_tls_key" {
  secret_id = "schoolrail/${local.environment}/vault/tls-key"
}
