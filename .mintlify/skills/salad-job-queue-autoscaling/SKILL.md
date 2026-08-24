---
name: salad-job-queue-autoscaling
description:
  Create or discover a SaladCloud Job Queue and configure or verify a queue-autoscaled Container Group, including scale
  from zero, worker idempotency, live quota, scaling observation, and safe cleanup. Do not use for direct gateway
  autoscaling or queue attachment by patch.
license: CC-BY-4.0
compatibility:
  Requires HTTPS access to the SaladCloud public API and a worker image containing the SaladCloud Job Queue Worker.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Configure Salad Job Queue autoscaling

## Invoke this skill when

The workload consists of retryable JSON jobs handled by the SaladCloud Job Queue Worker and worker count should follow
managed queue depth.

Do not invoke it for direct gateway traffic, non-idempotent/state-local work, or to add/change `queue_connection` on an
existing group; the current patch schema does not expose that field.

## Required environment variables

- `SALAD_API_KEY`, `SALAD_ORGANIZATION`, `SALAD_PROJECT`, `SALAD_QUEUE`, `SALAD_CONTAINER_GROUP`.
- `SALAD_CONTAINER_IMAGE`, `SALAD_QUEUE_PATH`, `SALAD_QUEUE_PORT`, `SALAD_MIN_REPLICAS`, `SALAD_MAX_REPLICAS`,
  `SALAD_DESIRED_QUEUE_LENGTH`.
- Hardware variables from the preflight skill and private-registry secret variables only when required.
- Optional `SALAD_WEBHOOK_SECRET` is consumed only by the application verifier; never print or return it.

## Read first

- [Job Queue autoscaling runbook](/agents/container-engine/configure-job-queue-autoscaling)
- [Job Queues](/container-engine/explanation/job-processing/job-queues)
- [Worker guide](/container-engine/how-to-guides/job-processing/queue-worker)
- [Autoscaling settings](/container-engine/reference/autoscaling/settings)

## Operations

- Operation IDs: `list_queues`, `get_queue`, `create_queue`, `update_queue`, `delete_queue`.
- Operation IDs: `list_container_groups`, `get_container_group`, `create_container_group`, `update_container_group`,
  `list_container_group_instances`, `delete_container_group`.
- Operation IDs: `list_queue_jobs`, `create_queue_job`, `get_queue_job`, `delete_queue_job`.
- Operation IDs: `get_quotas`, `list_gpu_classes`, `get_gpu_availability`, `get_cpu_availability`.

Canonical pages: [Queues](/reference/saladcloud-api/queues/list-queues),
[Create queue](/reference/saladcloud-api/queues/create-queue), [Read queue](/reference/saladcloud-api/queues/get-queue),
[Create group](/reference/saladcloud-api/container-groups/create-container-group), and
[Create job](/reference/saladcloud-api/queues/create-job).

## Procedure

1. Run Container Engine preflight using `max_replicas` for quota/capacity planning.
2. List queues/groups by exact name. Reuse only the intended exact resource; otherwise create once and verify.
3. Associate a queue only through `queue_connection` during `create_container_group`. For an already-associated group,
   read first and merge-patch `queue_autoscaler` only.
4. For `min_replicas: 0`, accept cold starts and require a readiness probe that reflects application readiness.
5. Submit a test job only with explicit intent. Poll queue length, group/instances, and job ID within a bounded budget.
6. Verify scaling stays between minimum/maximum, ready capacity appears, the job reaches its intended terminal status,
   and drained capacity returns to the minimum.

Query live: queue/group duplicates and association, current queue length/job events, group/autoscaler/version/status,
instance readiness, quota, GPU classes, and availability.

Workers must be idempotent because documented failures/interruptions can cause up to three retries after the first
attempt. Externalize job state and output before returning success. Do not invent an acknowledgment timeout. Validate
webhook signatures when used and keep the secret redacted.

## Safety and completion

Reconcile uncertain queue/group creates by exact name before retrying. Reconcile a job create only by its returned ID;
if no ID was returned, stop rather than resubmitting. Honor `Retry-After` and bound all polling. Do not automatically
resubmit a failed job. Queue/job/group deletion, cancellation, stop, and capacity reduction require explicit intent.
Before cleanup, read queue associations, jobs, group, and instances; stop if work or associations remain.

Success requires verified queue/group association, autoscaler values, live quota, observed bounded scaling, and job
outcome. Return IDs, statuses, counts, UTC times, and redacted settings. Escalate no-scaling with queue length,
association, readiness, worker logs, and capacity evidence.
