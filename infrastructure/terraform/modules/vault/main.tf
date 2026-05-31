resource "aws_kms_key" "vault_unseal" {
  description             = "KMS key for Vault auto-unseal"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = var.tags
}

resource "aws_kms_alias" "vault_unseal" {
  name          = "alias/${var.identifier}-vault-unseal"
  target_key_id = aws_kms_key.vault_unseal.key_id
}

resource "aws_iam_policy" "vault_unseal" {
  name = "${var.identifier}-vault-unseal"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [aws_kms_key.vault_unseal.arn]
      }
    ]
  })
}

resource "aws_iam_role" "vault" {
  name = "${var.identifier}-vault-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(var.oidc_provider_url, "https://", "")}:sub" = "system:serviceaccount:${var.namespace}:${var.service_account_name}"
          }
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "vault_unseal" {
  role       = aws_iam_role.vault.name
  policy_arn = aws_iam_policy.vault_unseal.arn
}

resource "aws_s3_bucket" "vault_storage" {
  bucket = "${var.identifier}-vault-storage"

  tags = var.tags
}

resource "aws_s3_bucket_versioning" "vault_storage" {
  bucket = aws_s3_bucket.vault_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "vault_storage" {
  bucket = aws_s3_bucket.vault_storage.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.vault_unseal.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "vault_storage" {
  bucket = aws_s3_bucket.vault_storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "vault_locks" {
  name         = "${var.identifier}-vault-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.vault_unseal.arn
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = var.tags
}

resource "kubernetes_namespace" "vault" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
}

resource "kubernetes_service_account" "vault" {
  metadata {
    name      = var.service_account_name
    namespace = var.namespace
    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.vault.arn
    }
  }

  depends_on = [kubernetes_namespace.vault]
}

resource "helm_release" "vault" {
  name       = var.identifier
  namespace  = var.namespace
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"
  version    = var.helm_chart_version

  values = [
    <<-VALUES
    global:
      enabled: true
    server:
      image:
        repository: hashicorp/vault
        tag: "${var.vault_version}"
      ha:
        enabled: true
        replicas: ${var.replicas}
        raft:
          enabled: true
          setNodeId: true
          config: |
            ui = true
            listener "tcp" {
              tls_disable = false
              address = "[::]:8200"
              cluster_address = "[::]:8201"
              tls_cert_file = "/vault/userconfig/vault-tls/tls.crt"
              tls_key_file = "/vault/userconfig/vault-tls/tls.key"
            }
            storage "raft" {
              path = "/vault/data"
              retry_join {
                leader_api_addr = "http://vault-0.vault-internal:8200"
              }
              retry_join {
                leader_api_addr = "http://vault-1.vault-internal:8200"
              }
              retry_join {
                leader_api_addr = "http://vault-2.vault-internal:8200"
              }
            }
            seal "awskms" {
              region     = "${var.aws_region}"
              kms_key_id = "${aws_kms_key.vault_unseal.key_id}"
            }
            service_registration "kubernetes" {}
      serviceAccount:
        create: false
        name: ${var.service_account_name}
      extraEnvironmentVars:
        VAULT_ADDR: "https://localhost:8200"
        VAULT_API_ADDR: "https://$(POD_IP):8200"
        VAULT_CLUSTER_ADDR: "https://$(HOSTNAME).vault-internal:8201"
        SKIP_CHOWN: "true"
      resources:
        requests:
          memory: "${var.resources_requests_memory}"
          cpu: "${var.resources_requests_cpu}"
        limits:
          memory: "${var.resources_limits_memory}"
          cpu: "${var.resources_limits_cpu}"
      auditStorage:
        enabled: true
        size: "${var.audit_storage_size}"
      dataStorage:
        enabled: true
        size: "${var.data_storage_size}"
        storageClass: "${var.storage_class}"
    ui:
      enabled: true
      serviceType: ClusterIP
      annotations: {}
    injector:
      enabled: true
      replicas: ${var.injector_replicas}
      resources:
        requests:
          memory: "256Mi"
          cpu: "100m"
        limits:
          memory: "512Mi"
          cpu: "500m"
    VALUES
  ]

  depends_on = [kubernetes_service_account.vault]
}

resource "kubernetes_secret" "vault_tls" {
  metadata {
    name      = "vault-tls"
    namespace = var.namespace
  }

  data = {
    "tls.crt" = var.tls_cert
    "tls.key" = var.tls_key
  }

  depends_on = [kubernetes_namespace.vault]
}

resource "kubernetes_network_policy" "vault" {
  metadata {
    name      = "vault-network-policy"
    namespace = var.namespace
  }

  spec {
    pod_selector = {
      match_labels = {
        app.kubernetes.io/name = "vault"
      }
    }

    ingress {
      from {
        namespace_selector = {}
      }
      ports {
        port     = "8200"
        protocol = "TCP"
      }
      ports {
        port     = "8201"
        protocol = "TCP"
      }
    }

    egress {
      to {
        ip_block {
          cidr = "0.0.0.0/0"
        }
      }
    }

    policy_types = ["Ingress", "Egress"]
  }

  depends_on = [kubernetes_namespace.vault]
}

output "vault_service_endpoint" {
  value = "https://${var.identifier}.${var.namespace}.svc.cluster.local:8200"
}

output "vault_ui_endpoint" {
  value = "https://${var.identifier}-ui.${var.namespace}.svc.cluster.local:8200"
}

output "kms_key_id" {
  value = aws_kms_key.vault_unseal.key_id
}

output "kms_key_arn" {
  value = aws_kms_key.vault_unseal.arn
}

output "iam_role_arn" {
  value = aws_iam_role.vault.arn
}

output "s3_bucket" {
  value = aws_s3_bucket.vault_storage.id
}

output "dynamodb_table" {
  value = aws_dynamodb_table.vault_locks.name
}

output "namespace" {
  value = var.namespace
}

output "service_account_name" {
  value = var.service_account_name
}

variable "identifier" {
  type = string
}

variable "namespace" {
  type    = string
  default = "vault"
}

variable "service_account_name" {
  type    = string
  default = "vault"
}

variable "aws_region" {
  type = string
}

variable "oidc_provider_arn" {
  type = string
}

variable "oidc_provider_url" {
  type = string
}

variable "vault_version" {
  type    = string
  default = "1.17.2"
}

variable "helm_chart_version" {
  type    = string
  default = "0.28.1"
}

variable "replicas" {
  type    = number
  default = 3
}

variable "injector_replicas" {
  type    = number
  default = 2
}

variable "resources_requests_memory" {
  type    = string
  default = "512Mi"
}

variable "resources_requests_cpu" {
  type    = string
  default = "250m"
}

variable "resources_limits_memory" {
  type    = string
  default = "2Gi"
}

variable "resources_limits_cpu" {
  type    = string
  default = "1"
}

variable "audit_storage_size" {
  type    = string
  default = "10Gi"
}

variable "data_storage_size" {
  type    = string
  default = "50Gi"
}

variable "storage_class" {
  type    = string
  default = "gp3"
}

variable "tls_cert" {
  type      = string
  sensitive = true
}

variable "tls_key" {
  type      = string
  sensitive = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
