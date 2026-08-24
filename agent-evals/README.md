# Agent operations evaluation corpus

This directory contains reviewable, provider-neutral scenarios for evaluating whether an AI agent follows the Salad
Container Engine runbooks and skills. It is not a live test harness and must not be used to mutate a SaladCloud account
without a dedicated credential, organization, project, and explicit authorization.

Each scenario declares the skill, repository sources, OpenAPI operations, live checks, safety behavior, forbidden
assumptions, and observable success criteria expected from an agent response. Example names and values are fictional.

Run the structural check from the repository root:

```bash
npm run validate:agent-operations
```

The check parses this YAML, confirms required source files, validates every declared operation ID against the current
public and IMDS OpenAPI specifications, and also validates the runbook/skill structure. Evaluation runners added later
should score evidence and stop behavior, not merely whether an agent issued a request.
