---
name: salad-transcription-lite-job
description:
  Submit, monitor, retrieve, or explicitly cancel one Salad Transcription Lite job at the fixed `transcription-lite`
  endpoint, rejecting primary-only fields and preventing uncertain duplicate submission. Do not use for the primary
  Transcription API.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and an authorized organization.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Operate a Salad Transcription Lite job

## Invoke this skill when

The user intends to create, poll, retrieve, or explicitly cancel a job under `transcription-lite`, and every requested
field exists in the Lite schema.

Do not invoke it for primary-only LLM/insight features, uncertain duplicates, or unauthorized cancellation/replacement.

## Required environment variables

- `SALAD_API_KEY` and `SALAD_ORGANIZATION`.
- `SALAD_MEDIA_URL` only for a new submission; `SALAD_TRANSCRIPTION_LITE_JOB_ID` only after SaladCloud returns it or it
  is loaded from a trusted record.
- Optional caller-managed variables for approved Lite fields, non-secret correlation metadata, and webhook URI.
- Caller-defined polling attempt and elapsed-time limits.

Never expose credentials, complete signed/webhook URIs, metadata values, media, or transcription output unless
explicitly requested through an authorized channel.

## Read first

- [Lite submission and monitoring runbook](/agents/transcription-lite/submit-and-monitor-job)
- [Transcription preflight](/agents/transcription/choose-api-and-preflight)
- [Create Lite job](/reference/transcription-lite/inference_endpoints/create-an-inference-endpoint-job)
- [Get Lite job](/reference/transcription-lite/inference_endpoints/get-an-inference-endpoint-job)

## Operations

All operations below are from `api-specs/transcription-lite.json` and must use the `/transcription-lite` path:

- `get_inference_endpoint` — validate the fixed Lite endpoint.
- `get_inference_endpoint_jobs` — inspect paginated jobs, never as proof of idempotency.
- `create_inference_endpoint_job` — submit once.
- `get_inference_endpoint_job` — poll and verify the returned ID.
- `delete_inference_endpoint_job` — cancel only with explicit intent.

Canonical mutation pages: [Create](/reference/transcription-lite/inference_endpoints/create-an-inference-endpoint-job)
and [Delete](/reference/transcription-lite/inference_endpoints/delete-an-inference-endpoint-job).

## Procedure

1. Run preflight and confirm the path contains `/transcription-lite/`.
2. Reject primary-only and undocumented fields, including `audio_stream_index`, `multichannel`, and `enhanced_accuracy`;
   Lite currently supports the basic URL, language, file-return, timestamp, diarization, SRT, and translation-to-English
   inputs in its schema.
3. If a trusted job ID exists, get it rather than creating another.
4. Validate the complete Lite body, submit once, and persist response ID/Location.
5. Poll the exact ID within budget. Verify required `text`, `duration`, and `processing_time` plus requested output.
6. Before cancellation, re-read and require explicit intent; verify `cancelled` afterward.

Query live: endpoint metadata, job ID/state/events/timestamps/output, rate-limit response, and source accessibility. The
unconstrained Lite `language_code` string is not evidence that every language is supported.

## Safety and completion

No idempotency key is documented. Stop an uncertain create without ID; never automatically resubmit failed/cancelled
work. Honor `Retry-After` and bound reads. A `201` or `202` does not establish a terminal result.

Success is the returned Lite job reaching `succeeded` with required output, or an authorized cancellation reaching
`cancelled`. Return path, ID, events/times, redacted fields, poll budget, and unresolved state. Escalate incorrect
output or unresolved polling with the troubleshooting skill.
