---
name: salad
description:
  Start here for anything on SaladCloud — deploying, scaling, debugging, pricing, or picking a GPU for a container
  group; writing code or a Dockerfile that will run on Salad's interruptible consumer GPU nodes; sending AI Gateway
  requests; submitting transcription jobs; or migrating from RunPod, Vast.ai, or AWS Batch. Gives the platform model,
  source precedence, the facts agents get wrong, and routes to the specialist salad-* skills.
license: CC-BY-4.0
compatibility:
  Requires HTTPS access to docs.salad.com; the specialist skills additionally need the SaladCloud public API.
metadata:
  author: Salad Technologies
  version: '1.0'
---

# SaladCloud router

## Invoke this skill when

The task mentions SaladCloud, Salad Container Engine (SCE), Salad AI Gateway, Salad Transcription API or Transcription
Lite, S4 storage, `portal.salad.com`, `api.salad.com`, `ai.salad.cloud`, or a `Salad-Api-Key` header — or the user wants
to run something "on Salad". Read this skill once, then hand off to the specialist skill in the routing table.

Do not invoke it for the Salad desktop app that device owners ("chefs") run to earn; that is not a SaladCloud customer
surface and no API here controls it.

## Required environment

- `SALAD_API_KEY` for the public API, sent only in the `Salad-Api-Key` header. It belongs to one user and grants access
  to every organization, project, and container group that user can reach. Never print, log, or persist its value; refer
  to it by name.
- `SALAD_ORGANIZATION` and, for Container Engine, `SALAD_PROJECT`. The API addresses organizations and projects by
  **name** and has no operation that lists the organizations a key can access. Take names from the user or trusted
  configuration; never guess or enumerate.
- `SALAD_AI_GATEWAY_API_KEY` only for AI Gateway, sent as a Bearer token. It is a different credential from the public
  API key and is organization-specific; never substitute one for the other.

## Read first

- [Agent Operations Overview](/agents/overview) — precedence, authorization boundaries, evidence to return.
- [Safety, Retries, and Freshness](/agents/reference/safety-retries-and-freshness) — retry, verification, and stop rules
  that apply to every operation below.
- [Using the API](/reference/api-usage) — authentication and key rotation.

## The platform in ten sentences

1. SaladCloud runs containers on consumer-owned gaming PCs (Windows hosts running Linux containers under WSL2), not in a
   data center; every instance is interruptible with no warning and is reallocated automatically to another node of the
   same GPU class.
2. The unit of deployment is a **container group**: one image, a hardware spec, a replica count, inside a project,
   inside an organization. The platform keeps the replica count by creating and purging **instances**.
3. Local disk is ephemeral and per instance; nothing written inside a container survives reallocation. Durable state
   goes to the user's own storage, S4, or a queue.
4. Images pull onto each node separately, so image size is cold-start time. Compressed images must be at most 35 GB and
   must be `linux/amd64`; ARM and Windows containers are not supported.
5. Inbound traffic reaches a group through the **Container Gateway** on exactly one port; the container must listen on
   IPv6. Authenticated networking is recommended and uses the same `Salad-Api-Key` header.
6. A running container learns about itself through **IMDS** at `169.254.169.254` (status, identity token, and a
   reallocate request) and reports health through startup, liveness, and readiness probes.
7. GPU groups choose a **priority**: high, medium, low, or batch (shown as "Lowest"); lower priority is cheaper and is
   preempted by higher. CPU-only groups always run at the lowest priority.
8. Billing is by replica running time; the organization's **replica quota** counts every group's replicas (or
   autoscaling maximum) whether the group is running or stopped, and one group cannot exceed 500 replicas.
9. Availability, prices, GPU classes, quotas, and instance state are live values; retrieve them immediately before a
   decision and never treat an example or a cached number as current.
10. Cold starts take minutes, single replicas have no failover, and network throughput varies node to node — design for
    retries and run at least two replicas.

## Source precedence

1. A live API response for current state, availability, quota, models.
2. The current OpenAPI specification (`api-specs/salad-cloud.yaml`, `salad-cloud-imds.yaml`, `transcribe.json`,
   `transcription-lite.json`) for paths, operation IDs, schemas, required fields, enums.
3. The applicable agent runbook and specialist skill for procedure and safety boundaries.
4. Canonical documentation for product behavior; `docs.salad.com/llms.txt` indexes it and any page is available as
   Markdown by appending `.md` to its URL.
5. Examples only as illustration. When a live response and a document disagree, use the live response and report the
   discrepancy.

## Route to a specialist skill

| The user wants to…                                                | Load                                                               | Runbook                                                                                     |
| ----------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Confirm org/project, quota, GPU class, availability before acting | `salad-container-engine-preflight`                                 | [Discover scope and preflight](/agents/container-engine/discover-scope-and-preflight)       |
| Create a container group or change an existing one                | `salad-container-engine-deploy`                                    | [Deploy or update](/agents/container-engine/deploy-or-update-container-group)               |
| Start, stop, scale, read instances, tail logs                     | `salad-container-engine-operate`                                   | [Monitor and operate](/agents/container-engine/monitor-and-operate-container-group)         |
| Find out why a group is not running, pulling, or passing probes   | `salad-container-engine-troubleshoot`                              | [Troubleshoot](/agents/container-engine/troubleshoot-container-group)                       |
| Set up a job queue and scale on queue depth                       | `salad-job-queue-autoscaling`                                      | [Configure job queue autoscaling](/agents/container-engine/configure-job-queue-autoscaling) |
| Send a chat completion through Salad AI Gateway                   | `salad-ai-gateway-request`                                         | [Select a model and send a request](/agents/ai-gateway/select-model-and-send-request)       |
| Diagnose a failed AI Gateway request                              | `salad-ai-gateway-troubleshoot`                                    | [Troubleshoot a request](/agents/ai-gateway/troubleshoot-request)                           |
| Choose Transcription API vs Transcription Lite                    | `salad-transcription-preflight`                                    | [Choose API and preflight](/agents/transcription/choose-api-and-preflight)                  |
| Submit and monitor a transcription job                            | `salad-transcription-job` or `salad-transcription-lite-job`        | [Submit and monitor](/agents/transcription/submit-and-monitor-job)                          |
| Diagnose a stuck or failed transcription job                      | `salad-transcription-troubleshoot`                                 | [Troubleshoot a job](/agents/transcription/troubleshoot-job)                                |
| Write a Dockerfile or service that will behave well on Salad      | this skill's "Building for Salad" section, then the pages it links | —                                                                                           |

Load exactly one specialist skill per task step. Preflight is not optional: run it before any create, update, scale, or
billable request.

## Facts agents get wrong

These are verified behaviors of the current platform. When one of them surprises the user, cite it rather than
re-deriving it.

| Area       | Fact                                                                                                                                                                                       |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Updates    | A container group update is an RFC 7386 merge patch, but `environment_variables` is **replaced, not merged** — send the complete map every time.                                           |
| Updates    | Setting `replicas` puts scheduled scaling on hold; re-enable it explicitly if the user relies on it.                                                                                       |
| Updates    | A patch on a CPU-only group resets `container.priority` to batch; `networking` in a patch accepts only `port`; `image_caching` is ignored on write.                                        |
| Updates    | `autostart_policy` is a create-time intent that the platform flips to `false` once the group starts; a later read showing `false` is expected, not a lost setting. Use start/stop instead. |
| Names      | A deleted group's name stays taken for a minute or two (soft delete); a create that fails on the name right after a delete is not a permissions problem.                                   |
| Instances  | An invalid `container.command` does not fail the deploy: the instance sits in `creating` indefinitely with no failure event. Check the command before waiting on state.                    |
| Logs       | The first stdout line of a freshly started container is not ingested. Log entries carry no unique ID, and `receive_time` cannot be queried — window on emission time.                      |
| Quota      | Quota counts replicas of stopped groups and the autoscaling maximum, not just what is running.                                                                                             |
| Priority   | High priority prevents preemption **by other workloads** only; the node can still go offline. Priority is a `container.priority` field: `high`, `medium`, `low`, `batch`.                  |
| Images     | Over 35 GB compressed fails to pull. A pull that has been "Downloading" longer than about two minutes per GB usually means a slow node; reallocating is normal, not a defect.              |
| Gateway    | Container Gateway requires IPv6 inside the container and caps requests at 1 GB.                                                                                                            |
| AI Gateway | `/v1/models` answers without authentication, so a successful models call proves nothing about the key; only a completion does.                                                             |
| AI Gateway | Hosted models reason before answering unless `chat_template_kwargs.enable_thinking` is `false`; a small `max_tokens` without that flag returns an empty-looking answer.                    |
| AI Gateway | Uncertain completions cannot be reconciled after the fact — there is no status read — so never retry a timed-out billable completion without the user's approval.                          |

## Symptom → likely cause → next step

| Symptom                                              | Likely cause                                                | Next step                                                                                |
| ---------------------------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 401 or 403 on a read that should work                | Wrong key type, or org/project name mistyped                | Confirm `Salad-Api-Key` (not Bearer) and the exact names; read quotas with `get_quotas`. |
| 404 on an organization or project                    | Name guessed or from a different account                    | Stop; ask the user for the name. The API cannot list organizations for a key.            |
| 409 or "name taken" right after a delete             | Soft-delete window                                          | Wait one to two minutes or pick another name.                                            |
| Instances stuck in `creating`, logs stop after start | Invalid `container.command`, or a probe that can never pass | Fix the command or probe; do not extend the wait.                                        |
| Instances stuck in `downloading`                     | Large image or slow node                                    | Check image size; if under 35 GB, reallocate the instance or wait.                       |
| Env var missing after an update                      | `environment_variables` replaced by a partial map           | Re-send the full map via `update_container_group`; verify with `get_container_group`.    |
| Scheduled scaling stopped firing                     | A replicas write put it on hold                             | Re-enable scheduled scaling after the replicas change.                                   |
| Gateway 5xx or timeouts on every request             | App listening on IPv4 only, or wrong port                   | Enable IPv6 in the image; confirm the group's `networking.port`.                         |
| Requests dropped mid-flight                          | Instance reallocated                                        | Expected on this network; retry at the client and run more replicas.                     |
| Create rejected for quota                            | Stopped groups or autoscaling maxima are consuming quota    | Read `get_quotas`; delete unused groups or request an increase.                          |
| AI Gateway returns a 200 but no visible answer       | Model spent the token budget thinking                       | Set `enable_thinking: false` or raise `max_tokens`.                                      |

## Building for Salad (coding-agent guidance)

Until the dedicated `salad-container-image` skill ships, read these before writing a Dockerfile or service for Salad:
[what to know before deploying](/container-engine/explanation/core-concepts/faqs),
[IMDS](/container-engine/explanation/infrastructure-platform/imds),
[health probes](/container-engine/explanation/infrastructure-platform/health-probes),
[networking and IPv6](/container-engine/explanation/infrastructure-platform/networking),
[environment variables](/container-engine/how-to-guides/environment-variables),
[job queues and autoscaling](/container-engine/explanation/infrastructure-platform/autoscaling), and
[troubleshooting](/container-engine/how-to-guides/troubleshooting). The rules that follow from them: assume the process
dies without notice, keep no state on disk, make startup idempotent, listen on IPv6, keep the image small, and give
probes a path that reflects real readiness.

## Safety, retries, verification, escalation

- Read before every write, write once, then verify with a read of the same resource. A `2xx` on start, stop, delete, or
  an instance action means accepted, not done; poll instances or job status within a caller-defined budget.
- Never delete, stop, scale down, reallocate, recreate, cancel, or resubmit without the user's explicit intent for that
  specific target. Never repeat an uncertain non-idempotent or billable request.
- Retry only reads and idempotent requests, with bounded backoff, honoring `Retry-After`. Do not retry authentication,
  authorization, validation, or conflict failures.
- Stop when a required name, credential, or prior value is missing, when the polling budget is spent, or when the
  evidence points at a platform-side problem; then escalate with the troubleshooting runbook's support package and
  [SaladCloud support](/support).
- Success means the live resource matches the requested state, and the evidence returned to the user names the
  organization, project, resource, operations used, HTTP response classes, timestamps, and any unresolved state — with
  no credential values.
