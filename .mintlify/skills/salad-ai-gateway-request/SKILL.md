---
name: salad-ai-gateway-request
description:
  Discover live Salad AI Gateway models and send one authorized OpenAI-compatible chat completion with credential,
  privacy, billing, uncertain-retry, and response verification safeguards. Do not use for self-hosted models, account
  onboarding, load testing, or automatic repetition of uncertain billable work.
license: CC-BY-4.0
compatibility: Requires HTTPS access to Salad AI Gateway and an organization-specific AI Gateway key.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Send a Salad AI Gateway request

## Invoke this skill when

The user wants to discover available hosted models or send one chat completion through `https://ai.salad.cloud/v1`.

Do not invoke it to create credentials, operate a self-hosted Container Engine model, run unapproved load tests, or
repeat a request whose processing or charge is uncertain.

## Required environment variables

- `SALAD_AI_GATEWAY_API_KEY`: an organization-specific AI Gateway key sent only as an `Authorization: Bearer` token.
- Optional caller-approved model/input variables and an attempt/time budget.

Never use the regular user-level `SALAD_API_KEY` or `Salad-Api-Key` header for AI Gateway. Never expose the key, prompt,
conversation history, images, tools, generated output, or billing context.

## Read first

- [Select a model and send a request](/agents/ai-gateway/select-model-and-send-request)
- [Models reference](/ai-gateway/reference/models)
- [Pay-per-token onboarding](/ai-gateway/tutorials/pay-per-token-onboarding)
- [Safety, retries, and freshness](/agents/reference/safety-retries-and-freshness)

## Endpoints

- `GET /v1/models` — retrieve current model IDs immediately before selection.
- `POST /v1/chat/completions` — send one approved OpenAI-compatible model request.

The docs repository has no AI Gateway OpenAPI specification. Use only documented request fields and observed live
responses; do not infer support or retry guarantees from another provider.

## Procedure

1. Confirm the credential type, authorized content, expected output, streaming mode, and billable attempt budget.
2. Read the live model catalog and require the exact model ID. If it is absent, stop or request approval for an
   alternative.
3. Check current published rates when cost affects selection.
4. Send one minimal documented request. Keep all sensitive content out of logs and evidence.
5. Verify response class, exact model, output shape, UTC time, and usage metadata when returned.
6. Return redacted evidence or invoke the troubleshooting skill for a classified failure.

## Safety and completion

Retry the model-list read only for plausible transient failures with bounded backoff and `Retry-After`. Never
automatically retry a timed-out completion, transport/server failure after send, or partial stream: the prior request
can be billable and a new generation can differ. Stop on authentication, authorization, validation, absent-model,
sensitive content, or exhausted-budget failures.

Success means the exact model was live and one authorized request returned the expected response shape. Return endpoint,
model, streaming mode, response class, time, attempt count, usage when supplied, and unresolved state without secrets.
Escalate persistent service, rate-limit, billing/access, or response mismatches with safe identifiers and redacted error
structure.
