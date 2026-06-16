# Security, Compliance & Governance

Authentication, authorization, encryption, audit trail, GDPR, EU AI Act, and institutional compliance requirements.

---

## Principle

The platform processes commercially sensitive portfolio information, lease terms, and possibly personal data. **Security and governance are product requirements, not later add-ons.** The concept doc explicitly requires institutional-grade controls for data rooms and client access.

---

## Authentication

### Phase 1–2 (MVP)

| Aspect | Implementation |
|--------|---------------|
| Method | JWT with refresh tokens |
| Login | Email + password (bcrypt hashed) |
| Token storage | httpOnly cookie (preferred) or secure localStorage |
| Access token TTL | 30 minutes |
| Refresh token TTL | 7 days |
| MFA | Optional TOTP (recommended for admin users) |

### Phase 3+ (Enterprise)

| Aspect | Implementation |
|--------|---------------|
| SSO | OIDC / SAML integration (Azure AD, Okta) |
| MFA | Enforced for all users via SSO provider |
| Session | SSO-managed session with JWT bridge |

---

## Authorization (RBAC)

### Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access: user management, audit log, settings, all projects |
| `valuation_lead` | Create/manage projects, approve assumptions, trigger runs, export |
| `analyst` | Upload data, map fields, review extractions, view results |
| `viewer` | Read-only access to results and reports |
| `client_viewer` | Read-only access to specific project(s) only (Phase 3+) |

### Permission Model

```
Organisation
  └── Project (project-level permissions)
        └── Actions: create, read, update, delete, run, export, admin
```

- Users are assigned roles at the **organisation level** (global) and optionally at the **project level** (scoped).
- Project-level role overrides organisation-level role (more restrictive).
- PostgreSQL **row-level security** (RLS) enforces tenant isolation at the database level.

```sql
-- Row-level security policy
ALTER TABLE approved.projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY project_access ON approved.projects
  USING (organisation_id = current_setting('app.current_org_id')::uuid);
```

---

## Encryption

| Scope | Method |
|-------|--------|
| In transit | TLS 1.3 everywhere (API, database, Redis, S3) |
| At rest — database | PostgreSQL TDE or managed DB encryption (RDS/Azure) |
| At rest — files | S3 server-side encryption (SSE-S3 or SSE-KMS) |
| At rest — backups | Encrypted backup snapshots |
| Secrets | Environment variables via secrets manager (AWS Secrets Manager, Azure Key Vault) |
| Passwords | bcrypt with cost factor 12 |
| JWT signing | HMAC-SHA256 (dev) / RSA-256 (prod, enables key rotation) |

---

## Audit Trail

The audit trail is a core product feature — not just a security control.

### What Is Logged

| Event | Fields Captured |
|-------|-----------------|
| Data upload | User, file name, file type, timestamp |
| AI extraction | Document, prompt version, model version, confidence scores |
| Field approval/rejection | User, field, old value, new value, reason, timestamp |
| Assumption change | User, scenario, field, old value, new value, reason |
| Valuation run trigger | User, project, scenario, model version, timestamp |
| Report generation | User, run_id, format (PDF/Excel), template |
| Login / logout | User, IP, timestamp, success/failure |
| Permission change | Admin, target user, old role, new role |

### Immutability

```sql
-- Audit table: no UPDATE or DELETE allowed
CREATE TABLE audit.audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- ... fields ...
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Revoke modification privileges
REVOKE UPDATE, DELETE ON audit.audit_events FROM dcf_app_user;

-- Application-level: only INSERT queries on this table
```

### Retention

- Audit logs retained for the lifetime of the project + configurable retention period (minimum 7 years for institutional clients).
- Secure deletion: when a project is deleted, audit logs are archived to cold storage before source data is purged.

---

## Data Protection (GDPR)

| Principle | Implementation |
|-----------|---------------|
| **Data minimisation** | Only collect data necessary for valuation. No unnecessary personal data. |
| **Purpose limitation** | Data used solely for valuation and reporting. No secondary use without consent. |
| **Access controls** | RBAC + project-level permissions. Users see only their projects. |
| **Right to erasure** | Project deletion workflow: archive audit → purge source files → anonymise DB records. |
| **Data portability** | Excel export contains all project data in structured format. |
| **Processor agreements** | LLM providers (Azure OpenAI) require data processing addendum. |
| **Breach notification** | Incident response plan with 72-hour GDPR notification workflow. |

### Personal Data in Documents

Lease documents may contain personal data (tenant contact names, signatures). Mitigations:
- Documents stored encrypted in S3
- Access restricted to project members
- LLM extraction uses enterprise endpoints (no training on customer data)
- Original documents deletable independently of extracted data

---

## AI Governance

| Control | Implementation |
|---------|---------------|
| **Model inventory** | Registry of LLM models, versions, and deployment endpoints used |
| **Prompt version control** | Extraction prompts stored in version-controlled YAML files |
| **Evaluation datasets** | Growing dataset of human-reviewed extractions for quality monitoring |
| **Confidence thresholds** | Configurable per field; low-confidence fields require human review |
| **Human approval gates** | All AI-extracted data must be approved before entering calculations |
| **No training on client data** | Enterprise LLM endpoints only; explicit contractual prohibition |
| **Extraction lineage** | Every extracted value linked to: source document, page, quote, prompt version, model version |

---

## EU AI Act Readiness

The platform's AI extraction features likely fall under the EU AI Act. Preparation:

| Requirement | Approach |
|-------------|----------|
| **Transparency** | Users see confidence scores, source citations, and know when AI is involved |
| **Human oversight** | Mandatory human review for all AI-extracted data |
| **Risk management** | Documented risk assessment for extraction accuracy and failure modes |
| **Technical documentation** | Model cards for each LLM deployment, evaluation results, known limitations |
| **Monitoring** | Ongoing accuracy tracking via evaluation datasets |
| **Record keeping** | Audit trail captures AI decisions with full provenance |

---

## Professional Standards Compliance

The platform must align with valuation industry standards:

| Standard | Requirement | Platform Support |
|----------|-------------|-----------------|
| **RICS** | Professional judgement, transparent methodology | Assumption attribution, audit trail, methodology docs in reports |
| **IVS** | Model governance, professional review | Model versioning, human approval gates, run-level audit |
| **INREV** | Transparency, consistency, governance in NAV | Standardised reports, scenario comparison, data quality metrics |

---

## Infrastructure Security

| Control | Implementation |
|---------|---------------|
| **Network** | VPC isolation, private subnets for DB/Redis, public subnet for API only |
| **Firewall** | Security groups: API accepts HTTPS only, DB accepts connections from API subnet only |
| **Secrets management** | No secrets in code or environment files; use AWS Secrets Manager / Azure Key Vault |
| **Vulnerability scanning** | Automated container image scanning (Trivy) in CI pipeline |
| **Dependency audit** | `pip-audit` for Python, `npm audit` for frontend — run in CI |
| **Backup / restore** | Daily automated DB backups, tested restore procedure, RPO < 24h |
| **Incident response** | Documented runbook: detection → containment → eradication → recovery → lessons learned |
| **Logging** | Structured JSON logs, centralised (CloudWatch / Azure Monitor), no PII in logs |
