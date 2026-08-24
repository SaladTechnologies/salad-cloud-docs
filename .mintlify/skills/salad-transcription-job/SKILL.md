---
name: salad-transcription-job
description:
  Submit, monitor, retrieve, or explicitly cancel one primary Salad Transcription API job at the fixed `transcribe`
  endpoint, with uncertain-create protection and terminal-state verification. Do not use for Transcription Lite or to
  resubmit failed work automatically.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and an authorized organization.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Operate a primary Salad Transcription job

## Invoke this skill when

The user intends to create, poll, retrieve, or explicitly cancel a job under the primary `transcribe` endpoint.

Do not invoke it for Lite, unsupported fields, an uncertain duplicate, or cancellation/replacement without intent.

## Required environment variables

- `SALAD_API_KEY` and `SALAD_ORGANIZATION`.
- `SALAD_MEDIA_URL` only for a new submission; `SALAD_TRANSCRIPTION_JOB_ID` only after SaladCloud returns it or it is
  loaded from a trusted record.
- Optional caller-managed variables for approved input fields, non-secret correlation metadata, and webhook URI.
- Caller-defined polling attempt and elapsed-time limits.

Never expose credentials, complete signed/webhook URIs, metadata values, media, or transcript/output content unless the
user explicitly requests that content through an authorized channel.

## Read first

- [Primary submission and monitoring runbook](/agents/transcription/submit-and-monitor-job)
- [Transcription preflight](/agents/transcription/choose-api-and-preflight)
- [Create primary job](/reference/transcribe/inference_endpoints/create-an-inference-endpoint-job)
- [Get primary job](/reference/transcribe/inference_endpoints/get-an-inference-endpoint-job)

## Operations

All operations below are from `api-specs/transcribe.json` and must use the `/transcribe` path:

- `get_inference_endpoint` — validate the fixed endpoint.
- `get_inference_endpoint_jobs` — inspect paginated jobs, never as proof of idempotency.
- `create_inference_endpoint_job` — submit once.
- `get_inference_endpoint_job` — poll and verify the returned ID.
- `delete_inference_endpoint_job` — cancel only with explicit intent.

Canonical mutation pages: [Create](/reference/transcribe/inference_endpoints/create-an-inference-endpoint-job) and
[Delete](/reference/transcribe/inference_endpoints/delete-an-inference-endpoint-job).

## Procedure

1. Run preflight and confirm the exact path contains `/transcribe/`.
2. If a trusted job ID already exists, get it rather than creating another.
3. Validate the full body against `CreateSaladCloudTranscriptionAPIJob`. Only `input.url` is required; omitted
   `language_code` means automatic detection. Primary-only fields include `audio_stream_index`, `multichannel`, and
   `enhanced_accuracy`.
4. Submit once and persist response ID/Location.
5. Poll the exact ID until `succeeded`, `failed`, or `cancelled`, or until the bounded budget expires.
6. On success, verify required/requested output fields from the live response. For multichannel diarization, verify
   channel identifiers in timestamp segments. Treat file URLs as sensitive observed behavior because their output shape
   is not defined by the current schema.
7. Before cancellation, re-read and require explicit user intent; verify `cancelled` afterward.

Query live: endpoint metadata, job ID/state/events/timestamps/output, rate-limit response, and source accessibility.

## Safety and completion

The API documents no idempotency key. If create outcome is unknown and no ID was returned, stop instead of retrying.
Never automatically resubmit failed/cancelled work or use a new job as rollback. Honor `Retry-After` and bound read
polling. A `201` or `202` is not terminal success.

Success is the exact returned job reaching `succeeded` with required output, or an authorized cancellation reaching
`cancelled`. Return path, ID, status/events/times, redacted field names, poll budget, and unresolved state. Escalate
with the troubleshooting skill when terminal output is wrong or bounded polling cannot resolve the job.
