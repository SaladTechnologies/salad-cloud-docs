---
name: docs-validation
description:
  Validate SaladCloud documentation tutorials and how-to guides. Use when asked to validate, test, verify, or check
  documentation for accuracy, working code examples, correct API calls, or UI consistency. Supports both authenticated
  and unauthenticated validation modes.
---

# Documentation Validation Skill

Validates SaladCloud tutorials and how-to guides by **actually following them step-by-step** to ensure they work
end-to-end.

## Core Philosophy

**The best way to validate a tutorial is to follow it.** Don't just check syntax - actually attempt each step as a user
would. If a step fails or is unclear, that's a validation failure.

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

### End-to-End Walkthrough (Primary)

The most important validation - actually following the tutorial:

- Attempt each step as documented
- Execute API calls and verify responses
- Follow portal UI instructions in a real browser
- Verify the workflow achieves its stated goal
- Report any step that fails, is unclear, or produces unexpected results

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
- **Live execution** when credentials are available

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

### Full Walkthrough (Default)

Actually follows the tutorial end-to-end:

1. **tutorial-walkthrough-validator** - Attempts each step as a user would
2. **code-block-validator** - Validates code syntax
3. **api-validator** - Checks API examples against specs and executes them
4. **portal-validator** - Verifies UI instructions in real browser
5. **content-validator** - Checks freshness and terminology

This is the recommended mode - it catches issues that syntax checking misses.

### Quick Validation

Skips browser-based and live API checks:

- Code block validation (syntax only)
- API example validation (spec matching only)
- Content freshness check

Use when you don't have credentials or need fast feedback.

### Syntax-Only Validation

Just checks code block syntax:

- Python, Dockerfile, Bash, JSON, YAML
- No API or portal checks
- Fastest mode

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
| End-to-End   | FAIL   | 1      |
| Code Blocks  | PASS   | 0      |
| API Examples | WARN   | 2      |
| Portal UI    | FAIL   | 1      |
| Content      | PASS   | 0      |

## Walkthrough Results

| Step | Description             | Status | Notes                         |
| ---- | ----------------------- | ------ | ----------------------------- |
| 1    | Obtain API Key          | PASS   | Found in portal as documented |
| 2    | Deploy Container Image  | FAIL   | 400 error - missing field     |
| 3    | Select Multiple GPUs    | SKIP   | Depends on Step 2             |
| 4    | Check Deployment Status | SKIP   | No deployment to check        |

**End-to-End Result:** FAIL - Could not complete tutorial as written

## Issues

### WALK-001 (Failure)

**Step:** 2 - Deploy Container Image **Type:** API Error **Details:** POST request returned 400 Bad Request - response:
"autostart_policy is required" **Impact:** User cannot complete tutorial as written **Fix:** Add
`"autostart_policy": false` to the JSON example

### API-001 (Warning)

**Location:** Line 89 **Type:** Missing header **Details:** curl example missing Content-Type header **Fix:** Add
`-H "Content-Type: application/json"`

### UI-001 (Failure)

**Location:** Line 45, Step 3 **Type:** UI text mismatch **Details:** Button says "New Container Group", docs say
"Create Container Group" **Fix:** Update button text in documentation
```

## Specialized Agents

This skill coordinates several specialized validation agents:

- **tutorial-walkthrough-validator** - Actually follows the tutorial step-by-step (PRIMARY)
- **code-block-validator** - Validates code syntax and structure
- **api-validator** - Checks API examples against OpenAPI specs, executes when possible
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
