---
name: docs-validation
description:
  Validate SaladCloud documentation tutorials and how-to guides. Use when asked to validate, test, verify, or check
  documentation for accuracy, working code examples, correct API calls, or UI consistency. Supports both authenticated
  and unauthenticated validation modes.
---

# Documentation Validation Skill

Validates SaladCloud tutorials and how-to guides for accuracy, working code, and UI consistency.

## Quick Start

### Validate a single file

```text
Validate container-engine/tutorials/quickstart.mdx
```

### Validate all tutorials

```text
Validate all tutorials in container-engine/
```

### Validate changed files only

```text
Validate documentation files changed in this PR
```

## What Gets Validated

### Code Blocks

- Python syntax and imports
- Dockerfile instructions
- Bash/shell commands
- JSON/YAML validity

### API Examples

- curl commands match OpenAPI specs
- Required headers present
- Request bodies have required fields
- Endpoints exist

### Portal UI (with authentication)

- Navigation paths work
- Button/link text matches
- Form fields exist
- Screenshots match current UI

### Content Freshness

- Last updated dates
- Version references
- Terminology consistency
- External link validity

## Authentication Setup

For portal UI validation, set credentials as environment variables:

```bash
export MCPROXY_CREDENTIAL_SALAD_EMAIL="your-email@example.com"
export MCPROXY_CREDENTIAL_SALAD_PASSWORD="your-password"
```

The AI agent never sees actual credential values - only references them by name.

See [AUTH.md](AUTH.md) for detailed setup instructions.

## Validation Modes

### Full Validation

Runs all validators on specified files:

- Code block validation
- API example validation
- Portal UI validation (if credentials available)
- Content freshness check

### Quick Validation

Skips browser-based checks:

- Code block validation
- API example validation
- Content freshness check

### Auth-Only Validation

Only portal UI checks:

- Screenshot comparison
- Navigation verification
- Form field validation

## File Locations

### Tutorials

- `container-engine/tutorials/`
- `gateway-service/tutorials/`
- `transcription/tutorials/`

### How-to Guides

- `container-engine/how-to-guides/`
- `transcription/how-to-guides/`

### API Specs (for validation)

- `api-specs/salad-cloud.yaml`
- `api-specs/salad-cloud-imds.yaml`
- `api-specs/transcribe.json`
- `api-specs/s4.yml`

## Report Format

```markdown
# Validation Report: quickstart.mdx

## Summary

| Check        | Status | Issues |
| ------------ | ------ | ------ |
| Code Blocks  | PASS   | 0      |
| API Examples | WARN   | 2      |
| Portal UI    | FAIL   | 1      |
| Content      | PASS   | 0      |

## Issues

### API-001 (Warning)

**Location:** Line 89 **Type:** Missing header **Details:** curl example missing Content-Type header **Fix:** Add
`-H "Content-Type: application/json"`

### UI-001 (Failure)

**Location:** Line 45, Step 3 **Type:** UI text mismatch **Details:** Button says "New Container Group", docs say
"Create Container Group" **Fix:** Update button text in documentation
```

## Specialized Agents

This skill coordinates several specialized validation agents:

- **code-block-validator** - Validates code syntax and structure
- **api-validator** - Checks API examples against OpenAPI specs
- **portal-validator** - Browser-based UI validation
- **content-validator** - Freshness and terminology checks

## CI/CD Integration

```yaml
# GitHub Actions example
- name: Validate Documentation
  env:
    MCPROXY_CREDENTIAL_SALAD_EMAIL: ${{ secrets.DOCS_VALIDATOR_EMAIL }}
    MCPROXY_CREDENTIAL_SALAD_PASSWORD: ${{ secrets.DOCS_VALIDATOR_PASSWORD }}
  run: |
    claude "Validate changed MDX files in this PR"
```
