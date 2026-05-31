terraform {
  backend "s3" {
    bucket         = "schoolrail-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "schoolrail-terraform-locks"
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
  alias  = "us_east_1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west_1"
  region = "eu-west-1"
}

locals {
  environment = "production"
  primary_region   = "us-east-1"
  secondary_region = "eu-west-1"

  common_tags = {
    Environment = local.environment
    Project     = "schoolrail"
    ManagedBy   = "terraform"
  }
}

module "eks_primary" {
  source = "../../modules/eks"
  providers = {
    aws = aws.us_east_1
  }

  cluster_name    = "schoolrail-${local.environment}-${local.primary_region}"
  cluster_version = "1.29"
  vpc_id          = data.aws_vpc.primary.id
  subnet_ids      = data.aws_subnets.primary_private.ids
  kms_key_arn     = data.aws_kms_key.primary_eks.arn

  service_instance_types  = ["m6i.large", "m6a.large"]
  worker_instance_types   = ["c6i.large", "c6a.large", "c6g.large"]
  monitoring_instance_types = ["t3.medium"]

  service_desired_size  = 3
  service_min_size      = 3
  service_max_size      = 15
  worker_desired_size   = 5
  worker_min_size       = 3
  worker_max_size       = 30
  monitoring_desired_size = 2
  monitoring_min_size     = 2
  monitoring_max_size     = 5

  tags = local.common_tags
}

module "eks_secondary" {
  source = "../../modules/eks"
  providers = {
    aws = aws.eu_west_1
  }

  cluster_name    = "schoolrail-${local.environment}-${local.secondary_region}"
  cluster_version = "1.29"
  vpc_id          = data.aws_vpc.secondary.id
  subnet_ids      = data.aws_subnets.secondary_private.ids
  kms_key_arn     = data.aws_kms_key.secondary_eks.arn

  service_instance_types  = ["m6i.large", "m6a.large"]
  worker_instance_types   = ["c6i.large", "c6a.large", "c6g.large"]
  monitoring_instance_types = ["t3.medium"]

  service_desired_size  = 3
  service_min_size      = 3
  service_max_size      = 10
  worker_desired_size   = 3
  worker_min_size       = 2
  worker_max_size       = 20
  monitoring_desired_size = 2
  monitoring_min_size     = 2
  monitoring_max_size     = 3

  tags = local.common_tags
}

module "rds_primary" {
  source = "../../modules/rds"
  providers = {
    aws = aws.us_east_1
  }

  identifier       = "schoolrail-${local.environment}"
  vpc_id           = data.aws_vpc.primary.id
  subnet_ids       = data.aws_subnets.primary_database.ids
  allowed_security_groups = [module.eks_primary.cluster_security_group_id]

  instance_class           = "db.r6g.large"
  read_replica_instance_class = "db.r6g.large"
  read_replica_count       = 2
  allocated_storage        = 500
  max_allocated_storage    = 2000
  database_name            = "schoolrail"
  master_username          = "schoolrail_admin"
  master_password          = data.aws_secretsmanager_secret_version.rds_master_password.secret_string
  multi_az                 = true

  tags = local.common_tags
}

module "rds_secondary" {
  source = "../../modules/rds"
  providers = {
    aws = aws.eu_west_1
  }

  identifier       = "schoolrail-${local.environment}-dr"
  vpc_id           = data.aws_vpc.secondary.id
  subnet_ids       = data.aws_subnets.secondary_database.ids
  allowed_security_groups = [module.eks_secondary.cluster_security_group_id]

  instance_class           = "db.r6g.large"
  read_replica_count       = 1
  allocated_storage        = 300
  max_allocated_storage    = 1000
  database_name            = "schoolrail"
  master_username          = "schoolrail_admin"
  master_password          = data.aws_secretsmanager_secret_version.rds_master_password.secret_string
  multi_az                 = true

  tags = local.common_tags
}

module "redis_primary" {
  source = "../../modules/redis"
  providers = {
    aws = aws.us_east_1
  }

  identifier       = "schoolrail-${local.environment}"
  vpc_id           = data.aws_vpc.primary.id
  subnet_ids       = data.aws_subnets.primary_private.ids
  allowed_security_groups = [module.eks_primary.cluster_security_group_id]

  node_type               = "cache.r6g.large"
  num_shards              = 3
  replicas_per_shard      = 2
  multi_az_enabled        = true
  snapshot_retention_days = 7

  tags = local.common_tags
}

module "redis_secondary" {
  source = "../../modules/redis"
  providers = {
    aws = aws.eu_west_1
  }

  identifier       = "schoolrail-${local.environment}-dr"
  vpc_id           = data.aws_vpc.secondary.id
  subnet_ids       = data.aws_subnets.secondary_private.ids
  allowed_security_groups = [module.eks_secondary.cluster_security_group_id]

  node_type               = "cache.r6g.large"
  num_shards              = 2
  replicas_per_shard      = 2
  multi_az_enabled        = true
  snapshot_retention_days = 7

  tags = local.common_tags
}

module "rabbitmq_primary" {
  source = "../../modules/rabbitmq"
  providers = {
    aws = aws.us_east_1
  }

  identifier       = "schoolrail-${local.environment}"
  vpc_id           = data.aws_vpc.primary.id
  subnet_ids       = data.aws_subnets.primary_private.ids
  allowed_security_groups = [module.eks_primary.cluster_security_group_id]

  deployment_type = "eks"
  admin_password  = data.aws_secretsmanager_secret_version.rabbitmq_admin_password.secret_string
  multi_az        = true
  min_replicas    = 3
  max_replicas    = 9

  tags = local.common_tags
}

module "rabbitmq_secondary" {
  source = "../../modules/rabbitmq"
  providers = {
    aws = aws.eu_west_1
  }

  identifier       = "schoolrail-${local.environment}-dr"
  vpc_id           = data.aws_vpc.secondary.id
  subnet_ids       = data.aws_subnets.secondary_private.ids
  allowed_security_groups = [module.eks_secondary.cluster_security_group_id]

  deployment_type = "eks"
  admin_password  = data.aws_secretsmanager_secret_version.rabbitmq_admin_password.secret_string
  multi_az        = true
  min_replicas    = 3
  max_replicas    = 6

  tags = local.common_tags
}

module "vault_primary" {
  source = "../../modules/vault"
  providers = {
    aws = aws.us_east_1
  }

  identifier        = "schoolrail-${local.environment}"
  namespace         = "vault"
  service_account_name = "vault"
  aws_region        = local.primary_region
  oidc_provider_arn = module.eks_primary.oidc_provider_arn
  oidc_provider_url = module.eks_primary.oidc_provider_url

  vault_version       = "1.17.2"
  replicas            = 3
  injector_replicas   = 2
  resources_requests_memory = "1Gi"
  resources_requests_cpu    = "500m"
  resources_limits_memory   = "4Gi"
  resources_limits_cpu      = "2"
  data_storage_size    = "100Gi"
  tls_cert             = data.aws_secretsmanager_secret_version.vault_tls_cert.secret_string
  tls_key              = data.aws_secretsmanager_secret_version.vault_tls_key.secret_string

  tags = local.common_tags
}

module "vault_secondary" {
  source = "../../modules/vault"
  providers = {
    aws = aws.eu_west_1
  }

  identifier        = "schoolrail-${local.environment}-dr"
  namespace         = "vault"
  service_account_name = "vault"
  aws_region        = local.secondary_region
  oidc_provider_arn = module.eks_secondary.oidc_provider_arn
  oidc_provider_url = module.eks_secondary.oidc_provider_url

  vault_version       = "1.17.2"
  replicas            = 3
  injector_replicas   = 1
  resources_requests_memory = "512Mi"
  resources_limits_memory   = "2Gi"
  data_storage_size    = "50Gi"
  tls_cert             = data.aws_secretsmanager_secret_version.vault_tls_cert.secret_string
  tls_key              = data.aws_secretsmanager_secret_version.vault_tls_key.secret_string

  tags = local.common_tags
}

data "aws_vpc" "primary" {
  provider = aws.us_east_1
  tags = {
    Name = "schoolrail-${local.environment}-vpc"
  }
}

data "aws_subnets" "primary_private" {
  provider = aws.us_east_1
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.primary.id]
  }
  tags = {
    Tier = "private"
  }
}

data "aws_subnets" "primary_database" {
  provider = aws.us_east_1
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.primary.id]
  }
  tags = {
    Tier = "database"
  }
}

data "aws_vpc" "secondary" {
  provider = aws.eu_west_1
  tags = {
    Name = "schoolrail-${local.environment}-vpc"
  }
}

data "aws_subnets" "secondary_private" {
  provider = aws.eu_west_1
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.secondary.id]
  }
  tags = {
    Tier = "private"
  }
}

data "aws_subnets" "secondary_database" {
  provider = aws.eu_west_1
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.secondary.id]
  }
  tags = {
    Tier = "database"
  }
}

data "aws_kms_key" "primary_eks" {
  provider   = aws.us_east_1
  key_id     = "alias/eks-${local.environment}"
}

data "aws_kms_key" "secondary_eks" {
  provider   = aws.eu_west_1
  key_id     = "alias/eks-${local.environment}"
}

data "aws_secretsmanager_secret_version" "rds_master_password" {
  provider  = aws.us_east_1
  secret_id = "schoolrail/${local.environment}/rds/master-password"
}

data "aws_secretsmanager_secret_version" "rabbitmq_admin_password" {
  provider  = aws.us_east_1
  secret_id = "schoolrail/${local.environment}/rabbitmq/admin-password"
}

data "aws_secretsmanager_secret_version" "vault_tls_cert" {
  provider  = aws.us_east_1
  secret_id = "schoolrail/${local.environment}/vault/tls-cert"
}

data "aws_secretsmanager_secret_version" "vault_tls_key" {
  provider  = aws.us_east_1
  secret_id = "schoolrail/${local.environment}/vault/tls-key"
}
