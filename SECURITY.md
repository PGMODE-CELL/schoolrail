# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x (latest) | ✅ Active development |
| 1.0.x | ✅ Security patches only |
| < 1.0 | ❌ |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, email the maintainers directly. You should receive a response within **24 hours**.

To report, include:
- Type (SQL injection, XSS, broken auth, tenant escape, etc.)
- Full paths of affected source files
- Step-by-step reproduction
- Proof-of-concept (if possible)
- Impact assessment

Email: `security@example.com`

## Our Security Architecture

### Authentication & Authorization
- **JWT RS256** with rotating signing keys managed by HashiCorp Vault
- Tokens auto-refresh every 15 minutes
- Blacklisted tokens checked via Redis
- OAuth 2.0 + OpenID Connect for SSO (Google, Microsoft, Azure AD)
- Role-based access: admin, driver, parent, superadmin
- Rate limiting: per-tenant, per-endpoint, sliding window (Redis Lua)

### Tenant Isolation
- **Database-per-tenant**: every school gets an isolated PostgreSQL database
- Connection pooling via PgBouncer (capped at 20 connections per tenant)
- No shared tables for tenant data
- Global registry (tenants, users) in separate Citus-distributed database
- Tenant ID validated on every request via dedicated middleware

### Data Protection
- **At rest**: AES-256 encryption on all databases (RDS + EBS encryption)
- **In transit**: TLS 1.3 required for all service-to-service communication
- **Secrets**: Dynamic database credentials via Vault (auto-rotated every 24h)
- **Backups**: Automated daily (30-day retention), encrypted, cross-region

### Network Security
- **Default deny** network policies in all K8s namespaces
- Services communicate via mTLS (Istio/Envoy sidecar)
- API Gateway is the only public-facing entry point
- WAF rules block SQL injection, XSS, path traversal
- DDoS protection via Cloudflare

### Audit & Monitoring
- **Immutable audit log**: every mutation logged with `(user_id, tenant_id, action, resource, timestamp, ip)`
- Audit logs written to append-only storage (S3 bucket with WORM policy)
- Prometheus alerts for: error rate > 1%, P99 latency > 1s, repeated auth failures
- Intrusion detection via Falco on K8s nodes

### Disclosure Policy

When we receive a security report:

1. **24h** — Confirm receipt and begin triage
2. **72h** — Patch developed and reviewed
3. **5 days** — Patch deployed to all supported versions
4. **7 days** — Public disclosure with CVE (if applicable)

## Hall of Fame

We maintain a private thank-you list for security researchers who report validated vulnerabilities. Contributors get:
- Name in release notes
- Priority review for future reports
- SchoolRail sticker pack
