---
name: salad-ai-gateway-troubleshoot
description:
  Diagnose Salad AI Gateway authentication, model, validation, billing/access, rate-limit, transport, streaming, or
  output failures from live evidence. Do not use to claim backend logs, expose content, or repeat an uncertain billable
  completion without explicit approval.
license: CC-BY-4.0
compatibility: Requires HTTPS access to Salad AI Gateway, the exact failing request context, and a bounded read budget.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Troubleshoot a Salad AI Gateway request

## Invoke this skill when

A model-list or chat-completion request fails, times out, is rate limited, disconnects, or returns unusable output.

Do not invoke it as authorization to expose secrets/content, inspect undocumented backend state, change billing, or
repeat uncertain work.

## Required environment variables

- `SALAD_AI_GATEWAY_API_KEY`, confirmed as an organization-specific AI Gateway key without revealing its value.
- Caller-approved variables for the exact endpoint, model, stream flag, UTC incident window, client/runtime versions,
  and attempt/time budget.

Never print the key, prompts, conversations, images, tools, output, or unrelated headers.

## Read first

- [AI Gateway troubleshooting runbook](/agents/ai-gateway/troubleshoot-request)
- [Select a model and send a request](/agents/ai-gateway/select-model-and-send-request)
- [Getting Started](/ai-gateway/tutorials/getting-started)
- [Safety, retries, and freshness](/agents/reference/safety-retries-and-freshness)

## Endpoints

- `GET /v1/models` — separate reachability/authentication and live model selection from completion failures.
- `POST /v1/chat/completions` — diagnostic calls are new billable work and require explicit approval.

No AI Gateway OpenAPI specification or completion-reconciliation endpoint is present in this repository. Do not invent
fields, backend logs, error meanings, retry guarantees, billing state, or the outcome of an interrupted request.

## Procedure

1. Capture redacted endpoint, model, stream flag, UTC time, response class/safe headers, client/runtime versions, and
   error structure.
2. Verify the base URL, Bearer authentication pattern, and live model list within a bounded read budget.
3. Compare only request field names/types with documented examples and the exact installed SDK version.
4. Classify configuration, authentication/authorization, unavailable model, validation, billing/access, rate limit,
   transport, service, stream handling, or output mismatch.
5. Retry reads only when safe. Run one minimal diagnostic completion only with approval and a defined success predicate.
6. Return classification, live evidence, verification, unavailable evidence, and escalation package.

## Safety and completion

Honor `Retry-After` and bound every retry. Never automatically retry authentication/validation failures, an uncertain
completion, or a partial stream. Stop for sensitive unredactable evidence, missing credential confirmation, absent
model, uncertain billing/outcome, or exhausted budget.

Success is an evidence-backed classification and verified next action, not merely a successful model-list read. Escalate
persistent service or output problems with endpoint, model, UTC window, safe identifiers, client/runtime versions,
response class, retry history, and redacted error structure.
