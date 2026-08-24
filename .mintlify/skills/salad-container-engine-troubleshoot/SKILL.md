---
name: salad-container-engine-troubleshoot
description:
  Diagnose one SaladCloud Container Group using configuration, instance state, controller events, application logs, live
  capacity constraints, and probe/network evidence; reallocate only for an evidence-backed isolated node condition. Do
  not use as blanket permission to mutate.
license: CC-BY-4.0
compatibility:
  Requires HTTPS access to the SaladCloud public API; IMDS reallocation additionally runs inside the affected instance.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Troubleshoot a Salad Container Engine group

## Invoke this skill when

The group fails/pends, instances remain allocating/downloading/creating, a running instance never becomes ready,
gateway/application failures occur, or equivalent instances show inconsistent performance.

Do not invoke it to label ordinary performance variation as infrastructure failure, churn nodes, or change/delete/stop
resources without explicit user intent.

## Required environment variables

- `SALAD_API_KEY`, `SALAD_ORGANIZATION`, `SALAD_PROJECT`, `SALAD_CONTAINER_GROUP`.
- `SALAD_LOG_START_TIME`, `SALAD_LOG_END_TIME`.
- `SALAD_INSTANCE_ID` only when retrieved live.
- Inside an instance, no public API key is required for IMDS; send the documented `Metadata` header and a non-secret
  reason. Never forward public API or registry credentials to IMDS.

## Read first

- [Troubleshooting runbook](/agents/container-engine/troubleshoot-container-group)
- [Canonical troubleshooting](/container-engine/how-to-guides/troubleshooting)
- [System events](/container-engine/explanation/container-groups/system-events)
- [IMDS reallocation guidance](/container-engine/how-to-guides/imds/imds-reallocate)

## Operations

- Operation IDs: `get_container_group`, `list_container_group_instances`, `get_container_group_instance`.
- Operation IDs: `query_log_entries`, `get_system_logs` (canonical page marks the latter deprecated).
- Operation IDs: `get_quotas`, `list_gpu_classes`, `get_gpu_availability`, `get_cpu_availability`.
- Operation ID: `reallocate_container_group_instance` for an authorized management-side reallocation.
- Operation ID: `get_status` to read current in-instance IMDS health before an authorized IMDS lifecycle action.
- Operation ID: `reallocate` for an authorized in-instance IMDS reallocation.

Canonical pages: [Group](/reference/saladcloud-api/container-groups/get-container-group),
[Instances](/reference/saladcloud-api/container-groups/list-container-group-instances),
[Logs](/reference/saladcloud-api/logs/query-log-entries),
[Management reallocation](/reference/saladcloud-api/container-groups/reallocate-container-group-instance), and
[IMDS status](/reference/imds/get-status), and [IMDS reallocation](/reference/imds/reallocate).

## Procedure

Follow the evidence order: group configuration/status; instance state; controller events; container logs; live
quota/availability/priority/hardware/countries; registry/image; startup/readiness/liveness; networking/queue; failure
classification; reallocation decision; escalation package.

Query live all current resource/instance/version/readiness data and incident-window evidence. For performance, compare
same image/version, GPU class, CPU/RAM/storage, countries, priority, input, and measurement across peers.

Reallocate only one isolated instance when equivalent peers succeed and evidence shows a persistent node-specific
failure against a real workload requirement. Preserve evidence and obtain explicit intent first. Configuration errors,
bad images, quota/allocation constraints, all-node failures, and unbenchmarked variance are not reallocation cases.

## Safety and completion

Retry reads only within a bounded budget. Re-read instance IDs before a lifecycle request and never loop reallocation.
After reallocation, list instances until replacement capacity satisfies the declared running/ready predicate; `202` or
IMDS `204` alone is not success.

Return a redacted escalation package with scope, group/version/status, instance/machine IDs, UTC times, events, log
excerpts, trace/request/job IDs when present, reproduction, recent changes, live constraints, and equivalent performance
comparisons. Stop for missing evidence/intent or an exhausted polling budget and contact support through the runbook.
