---
name: salad-container-engine-preflight
description:
  Preflight a SaladCloud Container Engine create, update, scale, or autoscaling task by validating caller-supplied
  scope, duplicate names, quota, hardware constraints, and live CPU or GPU availability. Do not use for other SaladCloud
  products or to mutate resources.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and caller-provided SaladCloud scope.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Salad Container Engine preflight

## Invoke this skill when

The task needs current organization/project validation, Container Group name reconciliation, quotas, GPU class UUIDs, or
CPU/GPU availability before a Container Engine mutation.

Do not invoke it to guess organization/project names, quote example capacity as current, or perform a write.

## Required environment variables

- Credential: `SALAD_API_KEY`.
- Scope: `SALAD_ORGANIZATION`, `SALAD_PROJECT`.
- Planned values as applicable: `SALAD_CONTAINER_GROUP`, `SALAD_REPLICAS`, `SALAD_CPU`, `SALAD_MEMORY_MB`,
  `SALAD_STORAGE_BYTES`, `SALAD_GPU_CLASS_ID`, `SALAD_PRIORITY`, `SALAD_COUNTRY_CODES`.

Never print, transmit outside `api.salad.com`, commit, or persist `SALAD_API_KEY`. Organization and project values must
come from the user, trusted configuration, or Portal; the public API has no list-organizations/list-projects operation.

## Read first

- [Scope and preflight runbook](/agents/container-engine/discover-scope-and-preflight)
- [API authentication](/reference/api-usage)
- [Safety, retries, and freshness](/agents/reference/safety-retries-and-freshness)

## Operations

- Operation ID: `get_quotas` — [Get Quotas](/reference/saladcloud-api/organizations/get-quotas)
- Operation ID: `list_container_groups` —
  [List Container Groups](/reference/saladcloud-api/container-groups/list-container-groups)
- Operation ID: `list_gpu_classes` — [List GPU Classes](/reference/saladcloud-api/organizations/list-gpu-classes)
- Operation ID: `get_gpu_availability` —
  [Get GPU Availability](/reference/saladcloud-api/organizations/get-gpu-availability)
- Operation ID: `get_cpu_availability` —
  [Get CPU Availability](/reference/saladcloud-api/organizations/get-cpu-availability)

## Procedure

1. Validate the supplied organization with `get_quotas` and project with `list_container_groups`.
2. Check the exact target name for an existing group; never treat a display name as an identifier.
3. Compute live quota headroom and include autoscaler maximum where applicable.
4. For GPUs, get current class UUIDs/constraints with `list_gpu_classes`, then query exact planned requirements with
   `get_gpu_availability`. For CPU-only work, use `get_cpu_availability`.
5. Report priority-specific availability and UTC observation time. Availability is an estimate, not a reservation.

Query live: quota/usage, group names, GPU class UUIDs and constraints, CPU/GPU availability, countries, priority, and
hardware filters. The current GPU class schema has no VRAM field; stop for an approved class mapping when VRAM is a hard
requirement.

## Safety and completion

Retry reads only for plausible transient failures with bounded backoff; honor `Retry-After` when present. Do not retry
unchanged `400`, `401`, or `403` failures. Stop for missing scope, ambiguous names, insufficient quota, invalid
constraints, unavailable required capacity, or unknown VRAM mapping.

Success means scope is validated, the duplicate decision is exact, quota is sufficient, and current availability was
queried for the intended configuration. Return redacted inputs, live results, and proceed/stop status; never treat
example resource names or identifiers as real.
