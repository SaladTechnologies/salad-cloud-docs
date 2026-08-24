---
name: salad-transcription-preflight
description:
  Choose between Salad Transcription API and Transcription Lite, validate the caller-supplied organization and media
  source, and reject features absent from the selected OpenAPI input schema. Use before submitting either product's
  asynchronous job; do not use to create, cancel, or retry a job.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and a caller-provided SaladCloud organization.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Preflight Salad Transcription APIs

## Invoke this skill when

The task needs a product decision, organization/product validation, media-access check, or request-field validation
before a primary or Lite transcription submission.

Do not invoke it to submit/cancel a job, guess an organization, or choose from static price/speed examples.

## Required environment variables

- `SALAD_API_KEY`, `SALAD_ORGANIZATION`, and `SALAD_MEDIA_URL`.
- Caller-selected `SALAD_TRANSCRIPTION_PRODUCT` with value `transcribe` or `transcription-lite`, unless feature
  requirements determine the choice.
- Optional non-secret feature inputs represented by caller-managed environment variable names.

Never print, transmit outside the authorized SaladCloud/media flow, commit, or persist API credentials, signed media
query parameters, webhook secrets, metadata values, media, or transcripts.

## Read first

- [Choose API and preflight](/agents/transcription/choose-api-and-preflight)
- [Transcription APIs overview](/transcription/explanation/overview)
- [API authentication](/reference/api-usage)
- [Safety, retries, and freshness](/agents/reference/safety-retries-and-freshness)

## Operations

- Primary Operation ID: `get_inference_endpoint`; exact path
  `GET /organizations/{organization_name}/inference-endpoints/transcribe` in `api-specs/transcribe.json`.
- Lite Operation ID: `get_inference_endpoint`; exact path
  `GET /organizations/{organization_name}/inference-endpoints/transcription-lite` in
  `api-specs/transcription-lite.json`.

The operation ID is shared; never select a path from the ID alone. Canonical job pages are under
[Transcription API](/reference/transcribe/inference_endpoints/create-an-inference-endpoint-job) and
[Transcription Lite](/reference/transcription-lite/inference_endpoints/create-an-inference-endpoint-job).

## Procedure

1. Require a trusted organization name and media URI; these specs do not enumerate organizations.
2. Select the exact product. Primary supports stream selection, multichannel, enhanced accuracy, and
   LLM/insight/custom-vocabulary/classification fields absent from Lite.
3. Read the selected endpoint and record current endpoint metadata/price description with a UTC timestamp.
4. Validate every request field against only that product's input schema. Allow `audio_stream_index`, `multichannel`,
   and `enhanced_accuracy` only on primary; reject them on Lite.
5. Confirm the source is externally downloadable without exposing signed URI components. Do not promise an undocumented
   minimum URL lifetime.
6. Return the exact product/path and proceed/stop decision.

Query live: endpoint metadata, access response, source accessibility, and rate-limit state. Static pricing, speed,
language, and example URLs are not current account facts.

## Safety and completion

Retry reads only for plausible transient failures with bounded backoff and `Retry-After` when present. Do not retry
unchanged schema, source-access, or authorization failures. This skill performs no SaladCloud mutation.

Success means the exact endpoint is readable, all intended fields exist in its schema, product choice is explicit, and
the source can be submitted safely. Stop for ambiguity or unsupported fields. Escalate persistent endpoint/schema
mismatch with exact path, UTC time, redacted field names, and problem details; never include secrets or media content.
