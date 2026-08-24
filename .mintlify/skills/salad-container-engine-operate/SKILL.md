---
name: salad-container-engine-operate
description:
  Read, start, stop, scale, and monitor one SaladCloud Container Group, including instance state, readiness, system
  events, application logs, bounded polling, and partial-success reporting. Do not use for creation or root-cause
  reallocation decisions.
license: CC-BY-4.0
compatibility: Requires HTTPS access to the SaladCloud public API and an authorized existing Container Group.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# Operate a Salad Container Engine group

## Invoke this skill when

The user asks for current state, instances, logs/events, scale-up/down, start, stop, or monitored convergence of one
known Container Group.

Do not invoke it to create a group, delete a resource, or diagnose/reallocate a suspected bad node without the
troubleshooting skill.

## Required environment variables

- `SALAD_API_KEY`, `SALAD_ORGANIZATION`, `SALAD_PROJECT`, `SALAD_CONTAINER_GROUP`.
- `SALAD_REPLICAS` for scaling.
- `SALAD_LOG_START_TIME` and `SALAD_LOG_END_TIME` for log/event queries.
- `SALAD_INSTANCE_ID` only after it is retrieved live when one instance must be inspected.

Never expose the API key or secret-bearing logs/environment values.

## Read first

- [Monitor and operate runbook](/agents/container-engine/monitor-and-operate-container-group)
- [Safety, retries, and freshness](/agents/reference/safety-retries-and-freshness)
- [Deployment lifecycle](/container-engine/explanation/container-groups/deployment-lifecycle)

## Operations

- Operation ID: `get_container_group`
- Operation ID: `list_container_group_instances`
- Operation ID: `get_container_group_instance`
- Operation ID: `update_container_group` for replicas
- Operation ID: `start_container_group`
- Operation ID: `stop_container_group`
- Operation ID: `query_log_entries`
- Operation ID: `get_system_logs` only when the deprecated canonical endpoint is specifically needed

Canonical pages: [Get group](/reference/saladcloud-api/container-groups/get-container-group),
[Instances](/reference/saladcloud-api/container-groups/list-container-group-instances),
[Scale](/reference/saladcloud-api/container-groups/update-container-group),
[Start](/reference/saladcloud-api/container-groups/start-container-group),
[Stop](/reference/saladcloud-api/container-groups/stop-container-group), and
[Logs](/reference/saladcloud-api/logs/query-log-entries).

## Procedure

1. Read the group and list instances before every decision/mutation.
2. Report desired `replicas` separately from actual allocating/downloading/creating/running/stopping and ready counts.
3. Before scale-up, query live quota/availability. Before scale-down or stop, require explicit user intent and account
   for active work/external state.
4. Perform one approved mutation.
5. Read group and instances afterward; poll only within the caller's attempt/time budget.
6. Query `deployment_controller`, `instance_controller`, and `container` log resources for a bounded UTC window when
   evidence is required.

Query live: group version/status/pending change, instance IDs/states/versions/readiness, quota/availability for
scale-up, queue/jobs before capacity reduction, and logs/events.

## Safety and completion

Start/stop return asynchronous acceptance; update returns a resource. Neither proves convergence. Re-read before
retrying any mutation, honor `Retry-After`, and do not extend polling indefinitely. Stop and scale-down always require
explicit intent; delete/reallocate/recreate/restart are outside this skill.

Success is the documented post-read predicate. Report partial success with exact counts; report pending with last state,
UTC time, and exhausted budget. Recover mistaken scaling/start/stop only with appropriate authorization. Escalate group
failure or unresolved convergence through the troubleshooting skill.
