resource "aws_db_subnet_group" "main" {
  name       = "${var.identifier}-subnet-group"
  subnet_ids = var.subnet_ids

  tags = var.tags
}

resource "aws_db_parameter_group" "postgres16" {
  name        = "${var.identifier}-pg16"
  family      = "postgres16"
  description = "PostgreSQL 16 parameter group for ${var.identifier}"

  parameter {
    name  = "shared_buffers"
    value = "{DBInstanceClassMemory*3/4}"
  }

  parameter {
    name  = "effective_cache_size"
    value = "{DBInstanceClassMemory*3/4}"
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "{DBInstanceClassMemory*1/16}"
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "wal_buffers"
    value = "{DBInstanceClassMemory*1/64}"
  }

  parameter {
    name  = "default_statistics_target"
    value = "100"
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1"
  }

  parameter {
    name  = "effective_io_concurrency"
    value = "200"
  }

  parameter {
    name  = "work_mem"
    value = "65536"
  }

  parameter {
    name  = "max_connections"
    value = "500"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,auto_explain"
  }

  parameter {
    name  = "track_io_timing"
    value = "1"
  }

  parameter {
    name  = "idle_in_transaction_session_timeout"
    value = "60000"
  }

  parameter {
    name  = "statement_timeout"
    value = "30000"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_checkpoints"
    value = "1"
  }

  parameter {
    name  = "log_lock_waits"
    value = "1"
  }

  parameter {
    name  = "log_temp_files"
    value = "0"
  }

  parameter {
    name  = "log_autovacuum_min_duration"
    value = "1000"
  }

  parameter {
    name  = "autovacuum_vacuum_scale_factor"
    value = "0.01"
  }

  parameter {
    name  = "autovacuum_analyze_scale_factor"
    value = "0.005"
  }

  parameter {
    name  = "autovacuum_vacuum_threshold"
    value = "50"
  }

  parameter {
    name  = "autovacuum_naptime"
    value = "30"
  }
}

resource "aws_kms_key" "rds" {
  description             = "RDS encryption key for ${var.identifier}"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = var.tags
}

resource "aws_db_instance" "primary" {
  identifier = "${var.identifier}-primary"

  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.instance_class

  db_name  = var.database_name
  username = var.master_username
  password = var.master_password

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  multi_az               = var.multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  parameter_group_name = aws_db_parameter_group.postgres16.name

  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:05:00-sun:06:00"

  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true
  delete_automated_backups   = false
  skip_final_snapshot        = false
  final_snapshot_identifier  = "${var.identifier}-final-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 15
  monitoring_role_arn                   = aws_iam_role.rds_enhanced_monitoring.arn

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = var.tags
}

resource "aws_db_instance" "read_replica" {
  count = var.read_replica_count

  identifier = "${var.identifier}-replica-${count.index + 1}"

  engine         = "postgres"
  engine_version = "16.3"
  instance_class = var.read_replica_instance_class

  replicate_source_db = aws_db_instance.primary.identifier

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  multi_az               = false
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  parameter_group_name = aws_db_parameter_group.postgres16.name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:05:00-sun:06:00"

  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true
  skip_final_snapshot        = true

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 15
  monitoring_role_arn                   = aws_iam_role.rds_enhanced_monitoring.arn

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = var.tags
}

resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "${var.identifier}-enhanced-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

resource "aws_security_group" "rds" {
  name        = "${var.identifier}-rds-sg"
  description = "RDS security group for ${var.identifier}"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
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

resource "aws_security_group_rule" "rds_replication" {
  count = var.multi_az ? 1 : 0

  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.rds.id
  security_group_id        = aws_security_group.rds.id
  description              = "RDS replication traffic"
}

output "primary_endpoint" {
  value = aws_db_instance.primary.endpoint
}

output "primary_arn" {
  value = aws_db_instance.primary.arn
}

output "read_replica_endpoints" {
  value = aws_db_instance.read_replica[*].endpoint
}

output "security_group_id" {
  value = aws_security_group.rds.id
}

output "kms_key_id" {
  value = aws_kms_key.rds.arn
}

output "parameter_group_name" {
  value = aws_db_parameter_group.postgres16.name
}

output "database_name" {
  value = var.database_name
}

output "master_username" {
  value = var.master_username
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

variable "instance_class" {
  type    = string
  default = "db.r6g.large"
}

variable "read_replica_instance_class" {
  type    = string
  default = "db.r6g.large"
}

variable "read_replica_count" {
  type    = number
  default = 0
}

variable "allocated_storage" {
  type    = number
  default = 200
}

variable "max_allocated_storage" {
  type    = number
  default = 1000
}

variable "database_name" {
  type = string
}

variable "master_username" {
  type = string
}

variable "master_password" {
  type      = string
  sensitive = true
}

variable "multi_az" {
  type    = bool
  default = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
