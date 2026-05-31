resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.identifier}-subnet-group"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "redis" {
  name        = "${var.identifier}-redis-sg"
  description = "ElastiCache Redis security group"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  ingress {
    from_port       = 6380
    to_port         = 6380
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_elasticache_parameter_group" "redis_cluster" {
  name        = "${var.identifier}-redis-cluster"
  family      = "redis7"

  parameter {
    name  = "cluster-enabled"
    value = "yes"
  }

  parameter {
    name  = "activerehashing"
    value = "yes"
  }

  parameter {
    name  = "lfu-log-factor"
    value = "10"
  }

  parameter {
    name  = "lfu-decay-time"
    value = "1"
  }

  parameter {
    name  = "timeout"
    value = "300"
  }

  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }

  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }

  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"
  }
}

resource "aws_kms_key" "redis" {
  description             = "ElastiCache encryption key for ${var.identifier}"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = var.tags
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id = var.identifier
  description         = "Redis cluster for ${var.identifier}"

  engine         = "redis"
  engine_version = "7.1"
  parameter_group_name = aws_elasticache_parameter_group.redis_cluster.name
  port                   = 6379
  transit_encryption_enabled = true
  at_rest_encryption_enabled = true
  kms_key_id                = aws_kms_key.redis.arn

  node_type            = var.node_type
  num_cache_clusters   = var.num_shards * var.replicas_per_shard
  num_node_groups      = var.num_shards
  replicas_per_node_group = var.replicas_per_shard - 1

  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  automatic_failover_enabled = true
  multi_az_enabled          = var.multi_az_enabled

  snapshot_retention_limit = var.snapshot_retention_days
  snapshot_window          = "03:00-04:00"
  maintenance_window       = "sun:05:00-sun:06:00"

  auto_minor_version_upgrade = true

  notification_topic_arn = var.sns_topic_arn

  tags = var.tags
}

resource "aws_elasticache_cluster" "replica" {
  count = var.create_replica_group ? 1 : 0

  cluster_id           = "${var.identifier}-replica"
  replication_group_id = aws_elasticache_replication_group.main.id

  tags = var.tags
}

output "primary_endpoint" {
  value = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "reader_endpoint" {
  value = aws_elasticache_replication_group.main.reader_endpoint_address
}

output "configuration_endpoint" {
  value = aws_elasticache_replication_group.main.configuration_endpoint_address
}

output "port" {
  value = 6379
}

output "security_group_id" {
  value = aws_security_group.redis.id
}

output "replication_group_id" {
  value = aws_elasticache_replication_group.main.id
}

output "arn" {
  value = aws_elasticache_replication_group.main.arn
}

variable "identifier" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "allowed_security_groups" {
  type = list(string)
}

variable "node_type" {
  type    = string
  default = "cache.r6g.large"
}

variable "num_shards" {
  type    = number
  default = 3
}

variable "replicas_per_shard" {
  type    = number
  default = 2
}

variable "multi_az_enabled" {
  type    = bool
  default = true
}

variable "snapshot_retention_days" {
  type    = number
  default = 7
}

variable "create_replica_group" {
  type    = bool
  default = false
}

variable "sns_topic_arn" {
  type    = string
  default = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}
