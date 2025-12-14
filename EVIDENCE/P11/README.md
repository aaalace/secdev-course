# P11 - DAST ZAP Baseline Reports

This directory contains OWASP ZAP baseline scan reports for the issue-lite service.

Reports are generated automatically by the CI workflow (`.github/workflows/ci-p11-dast.yml`).

## Files

- `zap_baseline.html` - Human-readable HTML report
- `zap_baseline.json` - Machine-readable JSON report

## Scan Target

- URL: `http://localhost:8000`
- Endpoints scanned: `/health`, `/issues`, and other discovered endpoints
