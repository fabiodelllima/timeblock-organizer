# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.7.x   | Yes       |
| < 1.7   | No        |

## Reporting a Vulnerability

> [!CAUTION]
> **Do not open public issues for security vulnerabilities.** Use the private disclosure process below.

To report a security vulnerability, email **fabiodelima@proton.me** with:

- Description of the vulnerability
- Steps to reproduce
- Estimated impact and severity
- Any suggested mitigation

### Response Timeline

- **Acknowledgment:** within 48 hours of report
- **Initial assessment:** within 7 days
- **Fix timeline by severity:**
  - Critical: patch within 7 days
  - High: patch within 14 days
  - Medium/Low: next scheduled release
- **Disclosure:** coordinated with reporter after fix is released
- **Credit:** reporters are credited in the CHANGELOG unless they request anonymity

## Threat Model

ATOMVS Time Planner is a **local-only desktop application**. It does not communicate over the network, does not run a server, and does not collect or transmit telemetry. This narrows the attack surface to two primary vectors:

### Supply Chain (Dependencies)

Third-party packages may introduce vulnerabilities transitively. Mitigation:

- **pip-audit** runs in every CI pipeline (`security:deps` job), checking all dependencies against the OSV database
- **Dependabot** monitors the GitHub mirror for known CVEs and opens automated PRs
- When a CVE has no upstream fix, the vulnerability is documented as a DT (Debt Item) in `docs/reference/technical-debt.md` with `--ignore-vuln` in the CI config and a justification for the temporary exception
- `requirements.txt` is generated from the active venv (`pip freeze`) and committed to enable reproducible dependency audits

### Input Validation (CLI and TUI)

User input flows through CLI arguments (Typer) and TUI form fields (Textual). Mitigation:

- All user input is validated in the Service Layer before reaching the database
- SQLModel/SQLAlchemy parameterized queries prevent SQL injection
- basedpyright in `standard` mode enforces type safety across the codebase, catching type confusion errors at development time
- Form fields validate formats (time, date, enum values) before submission

## Security Practices in CI/CD

### Static Application Security Testing (SAST)

Bandit (`security:bandit` job) scans all source code for common Python security issues: hardcoded credentials, use of `eval`/`exec`, insecure hashing, and other CWE-mapped patterns. The job produces a JSON report artifact and fails on high-severity findings.

### Software Composition Analysis (SCA)

pip-audit (`security:deps` job) checks installed packages against the OSV vulnerability database. The job runs independently (no build dependencies) and produces a JSON report. When a vulnerability has no available fix, the exception is documented with:

```yaml
# Documented in technical-debt.md as DT-XXX
pip-audit --ignore-vuln VULN-ID
```

### Type Safety as Security Boundary

basedpyright in `standard` mode (local) and mypy `--check-untyped-defs` (CI) serve as a security boundary by catching type confusion, None dereference, and unreachable code paths before they reach production.

### Pre-push Verification

A pre-push hook runs the complete test suite (unit, integration, BDD, e2e) and mypy type checking before any code reaches the remote. This prevents known-broken code from entering protected branches.

## Data Handling

| Data          | Location                                   | Scope |
| ------------- | ------------------------------------------ | ----- |
| Database      | `~/.local/share/atomvs/atomvs.db` (SQLite) | Local |
| Logs          | `~/.local/share/atomvs/logs/atomvs.jsonl`  | Local |
| Configuration | Project root (`pyproject.toml`)            | Local |

> [!NOTE]
> No data leaves the machine. There is no network communication, no telemetry, no analytics. All paths follow XDG Base Directory conventions (Linux).

- The database contains user-created routines, habits, tasks, and time logs
- Logs use JSON Lines format with rotation (10MB, 5 backups) and contain timestamps of user operations — no PII beyond what the user types

## Dependency Policy

- Direct dependencies are declared in `pyproject.toml` with minimum version pins
- The full resolved dependency tree is committed as `requirements.txt` for auditability
- Transitive dependency updates are tracked via Dependabot (GitHub mirror)
- CVEs without upstream fixes are documented as DTs with severity, justification, and workaround
- The Docker CI image is rebuilt periodically to incorporate security patches in system packages
