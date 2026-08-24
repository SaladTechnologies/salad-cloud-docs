---
name: salad-container-engine-deploy
description:
  Create a new SaladCloud Container Group or safely merge-patch one exact existing group, with duplicate avoidance,
  read-before-write, secret-safe request construction, rollout polling, and verification. Do not use for general
  monitoring or instance repair.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and an authorized Container Engine scope.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Deploy or update a Salad Container Engine group

## Invoke this skill when

The user intends to create a Container Group or update its supported configuration fields.

Do not invoke it to create a duplicate for an existing exact name, update an unsupported field, stop/delete a group, or
replace/reallocate an instance.

## Required environment variables

- Credential/scope: `SALAD_API_KEY`, `SALAD_ORGANIZATION`, `SALAD_PROJECT`, `SALAD_CONTAINER_GROUP`.
- Deployment: `SALAD_CONTAINER_IMAGE`, `SALAD_REPLICAS`, `SALAD_CPU`, `SALAD_MEMORY_MB`; optional `SALAD_STORAGE_BYTES`,
  `SALAD_GPU_CLASS_ID`, `SALAD_PRIORITY`, and `SALAD_COUNTRY_CODES`.
- Private registry when required: caller-selected `SALAD_REGISTRY_USERNAME`, `SALAD_REGISTRY_PASSWORD`,
  `SALAD_REGISTRY_TOKEN`, `SALAD_REGISTRY_SERVICE_KEY`, `SALAD_AWS_ACCESS_KEY_ID`, or `SALAD_AWS_SECRET_ACCESS_KEY`.

Never print, transmit outside the target API/registry flow, commit, or persist credential values. Refer to environment
variable names only in evidence.

## Read first

- [Deploy or update runbook](/agents/container-engine/deploy-or-update-container-group)
- [Preflight runbook](/agents/container-engine/discover-scope-and-preflight)
- [Create Container Group schema](/reference/saladcloud-api/container-groups/create-container-group)

## Operations

- Operation ID: `list_container_groups` — duplicate reconciliation.
- Operation ID: `get_container_group` — pre-write and post-write read.
- Operation ID: `create_container_group` — create only when the exact name is absent.
- Operation ID: `update_container_group` — supported merge patch.
- Operation ID: `list_container_group_instances` — rollout/readiness verification.

Canonical pages: [List](/reference/saladcloud-api/container-groups/list-container-groups),
[Get](/reference/saladcloud-api/container-groups/get-container-group),
[Create](/reference/saladcloud-api/container-groups/create-container-group),
[Update](/reference/saladcloud-api/container-groups/update-container-group), and
[Instances](/reference/saladcloud-api/container-groups/list-container-group-instances).

## Procedure

1. Invoke preflight. List exact names, then get the target if it exists.
2. If absent, validate all `ContainerGroupPrototype` required fields and create once.
3. If present, compare current/intended state. Build a minimal `application/merge-patch+json` body while preserving
   unrelated nested settings and environment variables.
4. Do not patch autostart policy, restart policy, queue connection, gateway auth, or gateway protocol: the current patch
   schema does not expose them. Networking patch exposes only `port`.
5. Read the group after the write. For runtime changes, list instances until `pending_change` clears and the required
   current-version running/ready capacity is reached.

Query live: target existence/config/version, quota, GPU classes, availability, instances, and readiness. Priority
request values are `container.priority`: `high`, `medium`, `low`, or `batch`.

## Safety and completion

Require explicit intent for scale-down or a change documented to restart/reallocate replicas. Reconcile an uncertain
create by exact name before any retry. Re-read before retrying a patch. Never delete a failed create automatically.

Success is the post-write resource matching intended fields plus the declared stopped/running and instance-readiness
predicate. On failure, restore only captured changed fields when authorized and possible; private-image rollback needs
usable prior credentials. Return versions, states, counts, timestamps, and redacted field names. Escalate persistent
failure with the troubleshooting runbook.
