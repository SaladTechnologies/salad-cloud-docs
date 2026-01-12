# Authentication Guide

## Overview

The docs validation workflow uses **mcproxy's secure credential handling** to authenticate with the SaladCloud portal. The AI agent never sees actual credential values - it only references them by name.

## How It Works

```
+------------------+     +-------------------+     +------------------+
|    AI Agent      |     |    MCP Server     |     |     Browser      |
|                  |     |    (mcproxy)      |     |                  |
| "Type credential |---->| Resolves name     |---->| Types actual     |
|  'salad_pass'"   |     | to actual value   |     | password         |
|                  |<----|                   |<----|                  |
| "Success"        |     | Scrubs response   |     | Page content     |
+------------------+     +-------------------+     +------------------+

Agent sees: "Typed credential 'salad_pass' into input[type='password']"
Agent never sees: The actual password value
```

## Setup

### Option 1: Environment Variables (Recommended)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export MCPROXY_CREDENTIAL_SALAD_EMAIL="your-email@example.com"
export MCPROXY_CREDENTIAL_SALAD_PASSWORD="your-password-here"
```

Then restart your terminal or run `source ~/.bashrc`.

### Option 2: CI/CD Environment

```yaml
# GitHub Actions
env:
  MCPROXY_CREDENTIAL_SALAD_EMAIL: ${{ secrets.DOCS_VALIDATOR_EMAIL }}
  MCPROXY_CREDENTIAL_SALAD_PASSWORD: ${{ secrets.DOCS_VALIDATOR_PASSWORD }}
```

### Verify Setup

The agent checks credentials before attempting login:

```
browser_has_credential("salad_email")    -> { exists: true }
browser_has_credential("salad_password") -> { exists: true }
```

If credentials are missing, the agent will:
1. Report which credentials are needed
2. Skip authenticated validations
3. Continue with unauthenticated checks

## Security Features

| Feature | Protection |
|---------|------------|
| Reference-only access | Agent uses names like "salad_password", never actual values |
| Response scrubbing | Any credential values in page content replaced with `[CREDENTIAL:name]` |
| Local storage | Credentials stored on your machine, never sent to AI providers |
| File permissions | `~/.mcproxy/credentials.json` created with 600 (owner read/write only) |

## Authentication Tiers

| Tier | Method | What It Validates |
|------|--------|-------------------|
| 0 - None | No auth | Code syntax, public pages, login page UI |
| 1 - API Key | `SALAD_API_KEY` env var | API endpoints, curl examples |
| 2 - Portal | `MCPROXY_CREDENTIAL_*` | Full portal UI, authenticated workflows |

## Login Flow

The portal-validator agent performs login as follows:

```
1. Navigate to https://portal.salad.cloud/login
2. Wait for email input field
3. Type email credential (agent never sees value)
4. Type password credential (agent never sees value)
5. Click submit button
6. Wait for dashboard to load
7. Verify login succeeded
```

If login fails:
- Agent reports the failure
- Takes screenshot for debugging
- Skips authenticated validations
- Continues with other checks

## Credential Requirements

### For Portal UI Validation

| Credential Name | Environment Variable | Purpose |
|-----------------|---------------------|---------|
| `salad_email` | `MCPROXY_CREDENTIAL_SALAD_EMAIL` | Portal login email |
| `salad_password` | `MCPROXY_CREDENTIAL_SALAD_PASSWORD` | Portal login password |

### For API Validation

| Variable | Purpose |
|----------|---------|
| `SALAD_API_KEY` | Validate API endpoints respond correctly |

## Troubleshooting

### "Missing credentials" error

```bash
# Verify env vars are set
env | grep MCPROXY_CREDENTIAL

# Should show:
# MCPROXY_CREDENTIAL_SALAD_EMAIL=...
# MCPROXY_CREDENTIAL_SALAD_PASSWORD=...
```

### "Login failed" error

Possible causes:
- Credentials are incorrect
- Portal login flow has changed (update selectors)
- Account requires MFA (not supported for automation)
- Account is locked or disabled

### Response shows `[CREDENTIAL:salad_password]`

This is expected behavior - it means response scrubbing is working correctly. The actual password appeared somewhere in page content and was filtered out before the agent could see it.

## Best Practices

1. **Use a dedicated test account** - Don't use your personal account for automated validation
2. **Minimal permissions** - Test account should only have read access if possible
3. **Rotate credentials** - Change password periodically
4. **Don't commit credentials** - Never put actual values in code or config files
5. **Use CI secrets** - In pipelines, always use secret management

## Without Authentication

If you can't or don't want to set up portal credentials, the validation workflow still provides value:

- Code block syntax validation
- API example validation against OpenAPI specs
- Content freshness checks
- Terminology consistency
- Public page UI validation (login page, marketing pages)

The agent will automatically skip authenticated checks and report what couldn't be validated.
