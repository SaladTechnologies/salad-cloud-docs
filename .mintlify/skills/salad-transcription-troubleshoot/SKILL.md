---
name: salad-transcription-troubleshoot
description:
  Diagnose a primary or Lite transcription job using the exact product path, job state/events, source accessibility,
  response problem details, output shape, and authorized webhook-receiver evidence. Do not use to infer backend logs,
  cancel work, or resubmit a job without explicit intent.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and an exact product plus trusted organization.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Troubleshoot Salad Transcription jobs

## Invoke this skill when

A primary or Lite job request fails, remains pending/running, reaches an unexpected terminal state, lacks required
output, or succeeds without an observed webhook.

Do not invoke it as permission to cancel or resubmit, or to claim service logs that the APIs do not expose.

## Required environment variables

- `SALAD_API_KEY`, `SALAD_ORGANIZATION`, and `SALAD_TRANSCRIPTION_PRODUCT`.
- `SALAD_TRANSCRIPTION_JOB_ID` or `SALAD_TRANSCRIPTION_LITE_JOB_ID` only from a trusted create response/record.
- Caller-defined incident UTC range and polling budget.

Never return API keys, complete signed/webhook URIs, sensitive metadata, media, transcripts, or unrelated customer data.

## Read first

- [Troubleshooting runbook](/agents/transcription/troubleshoot-job)
- [Product-selection preflight](/agents/transcription/choose-api-and-preflight)
- Primary [Get job](/reference/transcribe/inference_endpoints/get-an-inference-endpoint-job) or Lite
  [Get job](/reference/transcription-lite/inference_endpoints/get-an-inference-endpoint-job)

## Operations

Use the selected specification and exact path; all IDs are shared between primary and Lite:

- `get_inference_endpoint` — distinguish product/scope access from a job problem.
- `get_inference_endpoint_jobs` — paginated inventory only; no metadata filter or idempotency guarantee.
- `get_inference_endpoint_job` — authoritative current job state, events, timestamps, and output.
- `delete_inference_endpoint_job` — only for separately authorized cancellation.
- `create_inference_endpoint_job` — only for a separately authorized replacement after correction.

## Procedure

1. Resolve product from the trusted path, not the operation ID.
2. Read endpoint, then exact job. Preserve redacted ProblemDetails and event timestamps.
3. Compare echoed fields against the selected schema and verify source accessibility without exposing credentials. Treat
   `audio_stream_index`, `multichannel`, and `enhanced_accuracy` as primary-only.
4. Classify `pending`, `running`, `succeeded`, `cancelled`, or `failed`; event action names are not additional states.
5. For a primary multichannel job, verify channel identifiers in the requested word/sentence output rather than
   inferring success from echoed input.
6. For missing webhooks, verify job completion by GET and inspect only an authorized receiver. No webhook-delivery log
   or retry contract is defined by these specs.
7. Preserve evidence and build the runbook's escalation package.

Query live: endpoint access, exact state/events/timestamps/output, source reachability, receiver evidence, rate-limit
response, and server-provided retry guidance.

## Safety and completion

Retry only reads within a bounded budget and honor `Retry-After` when present. Never retry an uncertain create without
an ID, resubmit a terminal job automatically, or cancel without explicit intent and pre/post reads.

Success means the issue is classified from live evidence and the next action has a verifiable predicate. Escalate
unresolved jobs with organization, exact product/path, job ID/Location, UTC times/events, redacted field names, source
origin, webhook receiver result, response problem instance, and polling history. Clearly label unavailable backend
evidence instead of inventing it.
