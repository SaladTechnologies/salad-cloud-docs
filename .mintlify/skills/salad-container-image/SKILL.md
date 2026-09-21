---
name: salad-container-image
description:
  Write or adapt a Dockerfile, entrypoint, server, or worker so it runs correctly on SaladCloud's interruptible consumer
  GPU nodes — image constraints, IPv6 listening, IMDS, health probes, reallocation handling, the job queue worker
  contract, and the Salad-specific anti-patterns. Use before building an image for Salad Container Engine or when a
  container works locally but fails, loops, or returns 503 on Salad. Not for creating or operating the container group
  itself.
license: CC-BY-4.0
compatibility: Needs the target application's source or Dockerfile. No SaladCloud API access required.
metadata:
  author: Salad Technologies
  version: '0.1'
---

# Build a container image for Salad Container Engine

## Invoke this skill when

The user is writing, generating, or modifying an image, Dockerfile, server, entrypoint, or worker that will be deployed
as a SaladCloud container group; or a container that runs locally fails to start, restarts in a loop, is never reached
through the Container Gateway, or loses work on Salad.

Do not invoke it to create, update, scale, or troubleshoot the container group resource — use
`salad-container-engine-deploy`, `salad-container-engine-operate`, or `salad-container-engine-troubleshoot`. Preflight
with `salad-container-engine-preflight` before any deployment.

## Read first

- [Before you deploy](/container-engine/explanation/core-concepts/faqs) — the platform's own checklist.
- [IMDS](/container-engine/explanation/infrastructure-platform/imds) and the
  [IMDS API reference](/reference/imds/get-status).
- [Health probes](/container-engine/explanation/infrastructure-platform/health-probes), then
  [startup](/container-engine/explanation/infrastructure-platform/startup-probes),
  [liveness](/container-engine/explanation/infrastructure-platform/liveness-probes),
  [readiness](/container-engine/explanation/infrastructure-platform/readiness-probes).
- [Networking](/container-engine/explanation/infrastructure-platform/networking) and
  [Enabling IPv6](/container-engine/how-to-guides/gateway/enabling-ipv6).
- [Environment variables](/container-engine/how-to-guides/environment-variables),
  [Specifying a command](/container-engine/how-to-guides/specifying-a-command),
  [Container registries](/container-engine/explanation/infrastructure-platform/container-registries).
- [Job Queue Worker](/container-engine/how-to-guides/job-processing/queue-worker) for queue-driven workloads.
- [Troubleshooting](/container-engine/how-to-guides/troubleshooting) for what each failure looks like from outside.

Treat the current OpenAPI specification as authoritative for the container group fields named below
(`container.command`, `container.resources.storage_amount`, `networking.port`, probe objects). Read the live
documentation pages above; do not rely on this skill's summary when the two disagree.

## The runtime, in one screen

- **Host.** A consumer Windows PC running your `linux/amd64` container under WSL2 with hardware virtualization. No ARM,
  no Windows containers, no host access. GPU classes are selected NVIDIA and AMD consumer cards; a CUDA image needs an
  NVIDIA class and a ROCm image needs an AMD class of a matching architecture.
- **Lifecycle.** The instance can be interrupted at any moment with no signal you can rely on, and the platform will
  start a fresh instance elsewhere. Startup then happens again from the image: pull (cached on the network for up to 30
  days for public images), create, run. Cold start is minutes, not seconds.
- **Disk.** `container.resources.storage_amount` sizes an ephemeral disk (1 GB to 250 GB) that exists only for that
  instance. Nothing written to it survives reallocation or restart.
- **Network out.** Residential IP of the node; bandwidth is not metered. Hostname equals `SALAD_MACHINE_ID`.
- **Network in.** Only through the Container Gateway, only on the one `networking.port` you configure, only over HTTPS
  from the outside, delivered to your process over **IPv6**. Requests are capped at 1 GB. With authentication on
  (recommended), callers send `Salad-Api-Key`; with it off, your app must authenticate.
- **Identity.** Every container gets `SALAD_ORGANIZATION_NAME`, `SALAD_ORGANIZATION_ID`, `SALAD_PROJECT_NAME`,
  `SALAD_PROJECT_ID`, `SALAD_CONTAINER_GROUP_NAME`, `SALAD_CONTAINER_GROUP_ID`, `SALAD_INSTANCE_ID` (new on every
  start), `SALAD_MACHINE_ID`, and `HOSTNAME` (defaults to the instance ID).
- **Control from inside.** IMDS at `http://169.254.169.254` (port 80), header `Metadata: true`, proxies bypassed, no
  `X-Forwarded-*` headers. Operations (IMDS operation IDs): `get_status` (`ready`, `started`), `get_token` (a signed
  identity JWT for the instance), `reallocate`, `recreate`, `restart`, `get_deletion_cost`, `replace_deletion_cost`. The
  HTTP endpoints are the contract. SDKs exist (Python, JS, Java, Go, .NET) and wrap them; if you use one, verify its
  behavior against the IMDS API reference rather than assuming it.
- **Health.** Startup, liveness, and readiness probes over `exec`, `tcp`, `grpc`, or `http`. A failed startup or
  liveness probe reallocates the instance; a failed readiness probe keeps it running but removes it from the gateway.
- **Priority.** GPU groups run at `high`, `medium`, `low`, or `batch` priority and can be preempted by higher-priority
  work; CPU-only groups always run at the lowest priority.

## Procedure

1. **Establish the workload shape** with the user: HTTP service behind the gateway, queue worker, or batch job that
   pulls its own work. It decides the networking, probe, and exit-code design below.
2. **Pin the base image to the hardware.** Confirm the GPU class vendor and generation from the live class list (via the
   preflight skill), then choose CUDA or ROCm accordingly. RTX 5090 requires CUDA 12.8 or newer, and CUDA 12.8 images do
   not run on older GPUs; plan separate tags if both are targeted. Build for `linux/amd64` explicitly
   (`docker buildx build --platform linux/amd64`).
3. **Keep the image small and self-contained.** Hard limit 35 GB compressed. Pull time varies widely with the node's
   network; slower than two minutes per GB is the documented signal of a below-average node, not the expected case. Size
   still dominates time to first ready instance, so cut what you can. Order Dockerfile layers so weights and
   dependencies sit below code. Bake model weights in, or fetch them at startup from the user's storage or S4 behind a
   startup probe — never assume a previous instance's download is present.
4. **Make startup idempotent and the process long-lived.** The container is started many times per deployment. It must
   tolerate a cold disk, must not depend on state from a previous run, and must run a foreground process forever — an
   image whose `CMD` exits (an `ubuntu` base, a one-shot script) exits `0` and is restarted in a loop. If the user sets
   `container.command`, it replaces both `ENTRYPOINT` and `CMD`; the first element is the executable, the rest are
   arguments, and a command that cannot execute leaves the instance stuck in `creating` with no failure event. Verify
   the referenced binary and working directory exist in the image.
5. **Listen on IPv6 when the gateway is used.** Bind to `::` (or `[::]:PORT`), not `0.0.0.0` or `localhost`. For
   frameworks that cannot, add `socat TCP6-LISTEN:<gateway-port>,fork TCP4:127.0.0.1:<app-port>` in the entrypoint. The
   port the app listens on must equal `networking.port`. Verify with `netstat -topln` showing a `tcp6` line.
6. **Design probes to match real readiness.** Startup probe: pass only after models are loaded and the server answers;
   size `failure_threshold × period_seconds` to exceed the slowest expected start, or the platform reallocates a
   healthy-but-slow instance. Liveness probe: a cheap check that fails only on a genuine hang. Readiness probe: the
   check the gateway should trust; a readiness probe that passes early produces 503s for callers. Do not point `tcp`
   probes at a port that is not the gateway port.
7. **Handle reallocation as normal.** Retry at the client; checkpoint long work to the user's storage, S4, or a queue;
   on an unrecoverable local condition (bad node, missing GPU capability), call IMDS `reallocate` rather than exiting
   and hoping. Exit `137` after reallocate or restart is expected. Run at least two replicas (the docs recommend three
   for latency-sensitive work) — one replica has no failover.
8. **For queue workloads, implement the worker contract.** The Salad Job Queue Worker binary runs inside the container
   next to the app (s6-overlay or a supervising shell script), pulls jobs from the SaladCloud queue, and delivers each
   job as an HTTP request to the app on the local **port and path** configured in the container group's queue
   connection; the app's response body becomes the job output. The app therefore needs an HTTP handler on that
   port/path, and both processes must be supervised so the container exits if either dies. Quota counts the autoscaling
   maximum, so size `max_replicas` deliberately.
9. **Set deletion cost if scale-in order matters.** An instance mid-job can raise its deletion cost through IMDS
   `replace_deletion_cost` so intentional scale-down removes idle instances first. Use either IMDS or the API for this,
   not both.
10. **Test locally as Salad will run it.** `docker run --platform linux/amd64 -p [::1]:PORT:PORT <image>`, then curl
    over IPv6; run with a fresh, empty writable volume; kill the process mid-work and confirm a restart recovers;
    confirm the image starts with the exact `command` the group will use.
11. **Hand off.** Give the user the image reference, the port and path, the probe configuration, resource sizes (`cpu`,
    `memory`, `storage_amount`, `gpu_classes`), and the environment variables the group must set. Registry credentials
    and secrets go into the container group's environment or registry authentication, never into the image. Then load
    `salad-container-engine-preflight`.

## Dockerfile skeleton (HTTP service behind the gateway)

```dockerfile
# syntax=docker/dockerfile:1
FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04
# Dependencies below code so code changes do not invalidate the heavy layers.
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
# Bake weights (or fetch them in the entrypoint behind the startup probe).
COPY models/ /app/models/
COPY . .
ENV PORT=8000
EXPOSE 8000
# Bind IPv6. The container group's networking.port must be 8000.
CMD ["uvicorn", "main:app", "--host", "::", "--port", "8000"]
```

Pair it with: startup probe `http GET /ready` on 8000, `initial_delay_seconds` 30, `period_seconds` 10,
`failure_threshold` large enough for the model load; readiness probe `http GET /ready`; liveness probe `http GET /live`
that does not touch the model.

## Anti-patterns that fail on Salad specifically

| Anti-pattern                                                          | What happens on Salad                                     | Do instead                                                             |
| --------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------- |
| Bind to `0.0.0.0` or `localhost`                                      | Gateway 503; instance looks healthy from inside           | Bind to `::`, or bridge with `socat`                                   |
| Write results, caches, or checkpoints to local disk only              | Lost on every reallocation                                | Push to the user's storage, S4, or the queue result                    |
| Assume a stable IP, hostname, or instance ID                          | All three change on reallocation                          | Use `SALAD_CONTAINER_GROUP_ID` for identity; treat instances as cattle |
| `ubuntu`/`python` base with no long-running command                   | `Exited:0` then restart loop, then reallocation           | Run a foreground server or `sleep infinity` while debugging            |
| Download 20 GB of weights at start with a short startup probe         | Reallocated before it ever becomes ready                  | Bake weights, or lengthen the startup probe window                     |
| Readiness probe on a port or path that answers before the model loads | 503s for callers during warm-up                           | Readiness passes only when a real request would succeed                |
| Single replica for a service                                          | Downtime on every node event                              | Two or more replicas                                                   |
| `arm64` image built on Apple silicon                                  | `StartFailure`                                            | `--platform linux/amd64`                                               |
| CUDA image on an AMD class, or ROCm image on NVIDIA                   | `StartFailure` or runtime errors                          | Match image to the class vendor; verify with `nvidia-smi` / `rocminfo` |
| Image over 35 GB compressed                                           | Pull fails                                                | Trim layers, split weights, quantize                                   |
| Secrets baked into the image                                          | Distributed to every node that pulls it                   | Environment variables on the container group                           |
| Ignoring `137`                                                        | Misread as OOM when it was a requested reallocate/restart | Check System Events; raise memory only if no IMDS action was requested |

## Symptom → cause → fix

| Symptom                                                  | Likely cause                                             | Fix                                                                     |
| -------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------- |
| Loops between `downloading` and `allocating`             | Process exits immediately                                | Check System Events exit code; add a foreground process                 |
| `StartFailure:-1`                                        | Bad entrypoint/command, wrong arch, GPU runtime mismatch | Run the exact command locally; check arch and CUDA/ROCm vs class        |
| Stuck in `creating`, logs stop after "Instance Starting" | Invalid `container.command`                              | Fix the command array; the platform emits no failure event for this     |
| Stuck `downloading` beyond ~2 min/GB                     | Slow node or oversized image                             | Reallocate the instance; shrink the image                               |
| Gateway 503 while instance is `running`                  | IPv4-only bind, wrong port, or readiness passing early   | Bind `::`; match `networking.port`; fix readiness                       |
| Gateway 403                                              | Auth on, key missing/wrong; or brief route-table delay   | Send `Salad-Api-Key`; wait a few minutes; contact support if persistent |
| `Exited:137` with no OOM in logs                         | Requested reallocate/restart, or memory limit            | Check System Events before raising memory                               |
| Works on first instance, breaks after reallocation       | State on local disk or in memory only                    | Externalize state; make startup idempotent                              |
| Jobs never reach the app                                 | Worker port/path does not match the app's handler        | Align queue connection port/path with the app route; supervise both     |

## Safety, verification, escalation

- This skill does not call the SaladCloud API and needs no credentials; never place API keys, registry passwords, or
  tokens in a Dockerfile, image layer, or committed file. Refer to them by environment variable name.
- Do not remove or weaken a user's existing probes, resource limits, or authentication to make a deployment "work";
  explain the trade-off and stop for their decision.
- Verify claims about the live platform (GPU classes, prices, quota, current instance state) with the preflight skill
  and current API reads rather than from this document.
- Success is the image starting with the group's exact command, answering on IPv6 at the configured port, passing the
  probes as designed, and surviving a kill-and-restart without losing committed work.
- When a container fails in a way this skill does not explain, load `salad-container-engine-troubleshoot`, which builds
  the evidence package for [SaladCloud support](/support). Retry image pulls and starts only through the platform's own
  restart and reallocation; do not script rapid redeploy loops.
