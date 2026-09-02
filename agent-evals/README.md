# Agent operations evaluation corpus

This directory contains reviewable, provider-neutral scenarios for evaluating whether an AI agent follows the Container
Engine, AI Gateway, Transcription API, and Transcription Lite runbooks and skills. It is not a live test harness and
must not be used to mutate or bill a SaladCloud account without a dedicated credential and organization, a project where
the API requires one, and explicit authorization.

Each scenario declares the skill, repository sources, live checks, safety behavior, forbidden assumptions, and
observable success criteria expected from an agent response. Products with repository specifications declare OpenAPI
operation IDs in `required_operations`. Because AI Gateway does not currently have a repository OpenAPI specification,
its scenarios leave that list empty and declare the documented method and path in `required_endpoints` instead. Example
names and values are fictional.

Run the structural check from the repository root:

```bash
npm run validate:agent-operations
```

The check parses this YAML, confirms required source files, validates every declared operation ID against the relevant
current OpenAPI specification, restricts AI Gateway scenarios to documented endpoints, validates schema-derived
Transcription request examples, and validates the runbook/skill structure. Evaluation runners added later should score
evidence and stop behavior, not merely whether an agent issued a request.
