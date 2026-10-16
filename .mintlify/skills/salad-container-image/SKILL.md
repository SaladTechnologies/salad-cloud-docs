---
name: salad-container-image
description:
  Write or adapt a Dockerfile, entrypoint, server, or job queue worker so it runs correctly on SaladCloud's
  interruptible consumer GPU nodes — image constraints, the container command, IPv6 listening, IMDS, health probes,
  reallocation handling, the job queue worker contract, and the Salad-specific anti-patterns. Use before building an
  image for Salad Container Engine, or when a container works locally but fails, loops, returns 503, or loses jobs on
  Salad. Not for creating or operating the container group itself.
license: CC-BY-4.0
compatibility:
  Needs the target application's source or Dockerfile. Building needs no SaladCloud API access; testing on SaladCloud
  creates a billed container group.
metadata:
  author: Salad Technologies
  version: '0.2'
---

# Build a container image for Salad Container Engine

## Invoke this skill when

The user is writing, generating, or modifying an image, Dockerfile, server, entrypoint, or job queue worker that will be
deployed as a SaladCloud container group; or a container that runs locally fails to start, restarts in a loop, is never
reached through the Container Gateway, or loses work on Salad.

Do not invoke it to create, update, scale, or troubleshoot the container group resource — use
`salad-container-engine-deploy`, `salad-container-engine-operate`, or `salad-container-engine-troubleshoot`. Preflight
with `salad-container-engine-preflight` before any deployment.

## Read first

- [Before you deploy](/container-engine/explanation/core-concepts/faqs) — the platform's own checklist.
- [Cold Starts and Iterating Quickly](/container-engine/how-to-guides/cold-starts-and-iterating-quickly) — the short
  build, deploy and debug loop.
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
- [SSH and the web terminal](/container-engine/explanation/container-groups/ssh-and-terminal) for debugging inside a
  running instance.
- [Troubleshooting](/container-engine/how-to-guides/troubleshooting) for what each failure looks like from outside.

Treat the current OpenAPI specification as authoritative for the container group fields named below
(`container.command`, `container.resources.storage_amount`, `networking.port`, probe objects, `queue_connection`). Read
the live documentation pages above; do not rely on this skill's summary when the two disagree.

## The runtime, in one screen

- **Host.** A consumer Windows PC running your `linux/amd64` container under WSL2 with hardware virtualization. No ARM,
  no Windows containers, no host access. GPU classes are selected NVIDIA and AMD consumer cards; a CUDA image needs an
  NVIDIA class and a ROCm image needs an AMD class of a matching architecture.
- **Lifecycle.** The instance can be interrupted at any moment with no signal you can rely on, and the platform will
  start a fresh instance elsewhere. Startup then happens again from the image: pull (cached on the network for up to 30
  days for public images), create, run. Cold start is minutes, not seconds. A change to the image, command, environment
  variables, probes, or gateway settings restarts every instance onto the new version as its node next checks in; old
  and new never run side by side, and each instance downloads the whole new image again.
- **Disk.** `container.resources.storage_amount` sizes an ephemeral disk (1 GB to 250 GB) that exists only for that
  instance. Nothing written to it survives reallocation or restart.
- **Network out.** Residential IP of the node; bandwidth is not metered.
- **Network in.** Only through the Container Gateway, only on the one `networking.port` you configure, only over HTTPS
  from the outside, delivered to your process over **IPv6**. Requests are capped at 1 GB, and a response that takes
  longer than 100 seconds (the default) reaches the caller as 524. With authentication on (recommended), callers send
  `Salad-Api-Key`; with it off, your app must authenticate. For about a minute after an instance first reads ready, the
  gateway can still answer 503 for it.
- **Identity.** Every container gets `SALAD_ORGANIZATION_NAME`, `SALAD_ORGANIZATION_ID`, `SALAD_PROJECT_NAME`,
  `SALAD_PROJECT_ID`, `SALAD_CONTAINER_GROUP_NAME`, `SALAD_CONTAINER_GROUP_ID`, `SALAD_INSTANCE_ID` (new on every
  start), and `SALAD_MACHINE_ID`. The docs describe the hostname two ways (the machine ID; `HOSTNAME` defaulting to the
  instance ID, and overridable), so read the `SALAD_*` variables, not the hostname.
- **Command.** `container.command`, when set, replaces the image's `ENTRYPOINT` and `CMD` together and runs **without a
  shell**: the first word is the program and each later word is one argument. The node trims spaces around each word and
  drops empty words, which shifts the arguments after them. At most 100 words. An empty list (`[]`) goes back to the
  image's own command.
- **Logs.** Only stdout and stderr are collected; a log file inside the container is invisible. The first line a
  container prints after a restart or reallocation can be missing from the logs, so never make a single line the only
  sign of a failure.
- **Control from inside.** IMDS at `http://169.254.169.254` (port 80), header `Metadata: true`, proxies bypassed, no
  `X-Forwarded-*` headers. Operations (IMDS operation IDs): `get_status` (`ready`, `started`), `get_token` (a signed
  identity JWT for the instance), `reallocate`, `recreate`, `restart`, `get_deletion_cost`, `replace_deletion_cost`. The
  HTTP endpoints are the contract. SDKs exist (Python, JS, Java, Go, .NET) and wrap them; if you use one, verify its
  behavior against the IMDS API reference rather than assuming it.
- **Health.** Startup, liveness, and readiness probes over `exec`, `tcp`, `grpc`, or `http`. A failed startup or
  liveness probe reallocates the instance; a failed readiness probe keeps it running but removes it from the gateway. A
  group reads `running` as soon as any instance's container runs, ready or not; only each instance's ready state says it
  can serve.
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
   still dominates time to first ready instance, and every new version is downloaded in full by every instance, so cut
   what you can. Order Dockerfile layers so weights and dependencies sit below code. Bake model weights in, or fetch
   them at startup from the user's storage or S4 behind a startup probe — never assume a previous instance's download is
   present.
4. **Make startup idempotent and the process long-lived.** The container is started many times per deployment. It must
   tolerate a cold disk, must not depend on state from a previous run, and must keep a foreground process running — an
   image whose `CMD` exits (an `ubuntu` base, a one-shot script) exits `0` and, under the `always` restart policy,
   restarts in a loop. If the user sets `container.command`, write it as an array that starts with the program
   (`["python", "app.py", "--port", "8000"]`, not `["--port", "8000"]`). For shell syntax (`&&`, pipes, `$VAR`), call a
   shell yourself (`["bash", "-c", "..."]`) or put a script in the image. A command that cannot run fails at start, and
   the platform moves the instance to another node, over and over: the group never reaches `running`, and each attempt's
   logs stop after `Instance Starting`. Run the exact command array locally to prove the program, its arguments, and its
   working directory exist. Never put a secret in the command: the API returns it in full; use environment variables.
5. **Listen on IPv6 when the gateway is used.** Bind to `::` (or `[::]:PORT`), not `0.0.0.0` or `localhost`. Some
   servers take the bind address from an environment variable such as `HOSTNAME`; set it to `::` there. For frameworks
   that cannot bind IPv6, add `socat TCP6-LISTEN:<gateway-port>,fork TCP4:127.0.0.1:<app-port>` in the entrypoint. The
   port the app listens on must equal `networking.port`. Verify with `netstat -topln` showing a `tcp6` line. Work that
   can take longer than 100 seconds per request must stream its response or move to a job queue.
6. **Design probes to match real readiness.** Startup probe: pass only after models are loaded and the server answers;
   size `failure_threshold × period_seconds` to exceed the slowest expected start, or the platform reallocates a
   healthy-but-slow instance. Liveness probe: a cheap check that fails only on a genuine hang. Readiness probe: the
   check the gateway (and the job queue worker, step 8) should trust; a readiness probe that passes early produces 503s
   for callers. Do not point `tcp` probes at a port that is not the gateway port. In the container group definition,
   probes are top-level fields (`startup_probe`, `liveness_probe`, `readiness_probe`), not keys under `container`, and
   an `http` probe must carry `headers` even when it has none (`headers: []`); the API rejects it otherwise.
7. **Handle reallocation as normal.** Retry at the client; checkpoint long work to the user's storage, S4, or a queue;
   on an unrecoverable local condition (bad node, missing GPU capability), call IMDS `reallocate` rather than exiting
   and hoping. Exit `137` after reallocate or restart is expected. Replica count follows the workload shape from step 1:
   anything serving callers through the gateway needs at least two (three for latency-sensitive work), because one
   replica means downtime on every node event. For queue workers and batch jobs replica count is a throughput and cost
   decision, and a deliberate single-replica group per unit of work is a supported pattern — ask the user which shape
   applies instead of defaulting to a number.
8. **For queue workloads, implement the worker contract.** The Job Queue Worker (`salad-http-job-queue-worker`, from the
   [worker repository](https://github.com/SaladTechnologies/salad-cloud-job-queue-worker)) runs inside the container
   beside the app, takes jobs from the SaladCloud queue, and sends each job's input as an HTTP request to the app on the
   **port and path** of the container group's queue connection; the app's response body becomes the job's output, and a
   non-2xx response fails the attempt.
   - **Packaging.** One x86_64 build, no arm64. It depends on IMDS, so it runs only on SaladCloud; started anywhere else
     it logs `failed to fetch workload instance status … connection refused` over and over. Test the app's HTTP handler
     locally and the worker only in a deployed group. Supervise both processes (s6-overlay, or a start script that exits
     when either one exits) so a dead worker or app restarts the container.
   - **Start the worker after the app answers.** The worker takes jobs as soon as IMDS reports the instance ready. Give
     the group a readiness probe on the app's port, and also have the start script wait until the app answers its health
     path before it launches the worker: IMDS can report a new container ready before its probe has run. A worker that
     starts first spends all four attempts of the first job in about three seconds (`connection refused`) and fails it
     for good.
   - **Attempts.** A failed attempt is retried at once, about half a second later, four attempts in all, then the job is
     `failed`. That is not a backoff: a handler that needs a dependency to come up must wait for it itself, and every
     handler must be safe to run twice.
   - **Output cap.** A response over 10 MB counts as a failed attempt, so the job runs four times in full and then fails
     with no reason recorded. Write large results to the user's storage or S4 and return a reference.
   - **Work you cannot call back.** Cancelling a running job marks it `cancelled`, but the app still runs it to the end.
     A stopped or deleted group's worker can take jobs for some seconds afterwards, and those jobs, like any whose
     instance is interrupted, read `running` for about 5.5 minutes before they are retried. Make side effects
     idempotent.
   - **Logging.** The worker logs only errors by default, so a failed attempt leaves no line; have the app log each
     job's outcome itself. `SALAD_LOG_LEVEL=info` logs every job's full input, and `debug` logs the instance's identity
     token in full, both into the organization's container logs; avoid both where inputs are sensitive.
   - **Path.** The API stores the queue path exactly as given. Use a leading slash (`/generate`) and the exact route the
     app serves.
   - **Quota.** Quota counts the autoscaling maximum, so size `max_replicas` deliberately.
9. **Set deletion cost if scale-in order matters.** An instance mid-job can raise its deletion cost through IMDS
   `replace_deletion_cost` so intentional scale-down removes idle instances first. Use either IMDS or the API for this,
   not both.
10. **Test locally first, then on SaladCloud in the shortest loop.**
    - Locally: `docker run --platform linux/amd64 -p [::1]:PORT:PORT <image>`, then curl over IPv6; run with a fresh,
      empty writable volume; kill the process mid-work and confirm a restart recovers; confirm the image starts with the
      exact `command` the group will use. A GPU image may not run without a local GPU; then check what you can, such as
      that its imports load (`docker run --rm <image> python -c "import <module>"`).
    - On SaladCloud, only after the user agrees, since a group is billed while it runs: prove the plumbing with a small
      image that answers on the same port, paths, and probe path; switch to the real image once that works; while
      testing, run a few spare replicas and use whichever instance starts first, since nodes download at different
      speeds.
    - To debug a start failure by hand, set the command to `["sleep", "2147483647"]` (BusyBox `sleep` rejects
      `infinity`), remove the startup and liveness probes so they do not move the instance, connect over SSH, and run
      the entrypoint yourself. SSH needs the user's public key registered with SaladCloud and `/bin/sh` in the image;
      distroless and `scratch` images have neither a shell nor `sleep`, so keep a debug tag that has both. With the
      `saladcloud` CLI:

      ```sh
      saladcloud container-groups create my-debug --image <image> --wait -- sleep 2147483647
      saladcloud container-groups ssh my-debug          # a shell; run the image's entrypoint by hand
      saladcloud container-groups logs my-debug --since 1h --query 'resource.type != "container"'  # allocation, download, start, exit codes
      saladcloud container-groups instances list -c my-debug   # each instance's state, pull progress, and READY
      saladcloud container-groups delete my-debug
      ```

    Creating and operating the real group belongs to `salad-container-engine-deploy`.

11. **Hand off.** Give the user the image reference; the command, if any, as an array; the port and paths; the probe
    configuration (top-level fields, `headers: []` on `http` probes); resource sizes (`cpu`, `memory`, `storage_amount`,
    `gpu_classes`); the environment variables the group must set; and, for a queue worker, the queue port and path. Say
    which settings are fixed once the group is created — the gateway's authentication, protocol and timeouts (only its
    port can change later), the restart policy, and the queue connection — since changing one means a new group.
    Registry credentials and secrets go into the container group's environment or registry authentication, never into
    the image or the command. Then load `salad-container-engine-preflight`.

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
that does not touch the model. Every `http` probe carries `headers: []`.

## Start script skeleton (job queue worker)

```bash
#!/usr/bin/env bash
# start.sh: start the app, start the worker only once the app answers,
# and exit when either one exits so the platform restarts the container.
set -u
uvicorn main:app --host :: --port 8000 &
app=$!
until curl -fsS http://localhost:8000/health >/dev/null 2>&1; do
  kill -0 "$app" 2>/dev/null || exit 1
  sleep 1
done
/usr/local/bin/salad-http-job-queue-worker &
wait -n
exit 1
```

The image needs `bash` and `curl` (slim Python images have no `curl`; install it or poll with Python), the worker binary
extracted from the release's x86_64 archive, and `CMD ["/start.sh"]`. Pair it with a queue connection on port 8000 and
the handler's path, and a readiness probe `http GET /health` on 8000.

## Anti-patterns that fail on Salad specifically

| Anti-pattern                                                          | What happens on Salad                                                 | Do instead                                                             |
| --------------------------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Bind to `0.0.0.0` or `localhost`                                      | Gateway 503; instance looks healthy from inside                       | Bind to `::`, or bridge with `socat`                                   |
| Handle a long request synchronously                                   | 524 at the caller after 100 seconds                                   | Stream the response, or move the work to a job queue                   |
| Write results, caches, or checkpoints to local disk only              | Lost on every reallocation                                            | Push to the user's storage, S4, or the queue result                    |
| Log to a file                                                         | Nothing in SaladCloud's logs                                          | Log to stdout and stderr                                               |
| Assume a stable IP, hostname, or instance ID                          | All three change on reallocation                                      | Use `SALAD_CONTAINER_GROUP_ID` for identity; treat instances as cattle |
| `ubuntu`/`python` base with no long-running command                   | `Exited:0`, then a restart loop, then reallocation                    | Run a foreground server                                                |
| `sleep infinity` as a keep-alive or debug command                     | BusyBox rejects it; the instance moves from node to node              | `sleep 2147483647`                                                     |
| Shell syntax in `container.command`, or one word holding a whole line | No shell runs it: `$VAR` stays literal, a line becomes a program name | `["bash", "-c", "..."]`, or a script in the image                      |
| A secret in `container.command`                                       | Returned in full by the API                                           | Environment variables                                                  |
| Download 20 GB of weights at start with a short startup probe         | Reallocated before it ever becomes ready                              | Bake weights, or lengthen the startup probe window                     |
| Readiness probe that passes before the model loads                    | 503s for callers during warm-up                                       | Readiness passes only when a real request would succeed                |
| Queue worker started alongside the app with no gate                   | The first jobs fail all four attempts within seconds                  | Readiness probe, plus a start script that waits for the app            |
| Job response over 10 MB                                               | Run four times, then `failed` with no reason                          | Store the result; return a reference                                   |
| Job handler with side effects that are unsafe to repeat               | Retried, cancelled, and interrupted jobs run again or run anyway      | Idempotent handlers                                                    |
| Single replica for a service                                          | Downtime on every node event                                          | Two or more replicas                                                   |
| `arm64` image built on Apple silicon                                  | `StartFailure`                                                        | `--platform linux/amd64` (the queue worker ships for x86_64 only)      |
| CUDA image on an AMD class, or ROCm image on NVIDIA                   | `StartFailure` or runtime errors                                      | Match image to the class vendor; verify with `nvidia-smi` / `rocminfo` |
| Distroless or `scratch` image as the only tag                         | No SSH shell and no `sleep` to debug with                             | Keep a debug tag with a shell                                          |
| Image over 35 GB compressed                                           | Pull fails                                                            | Trim layers, split weights, quantize                                   |
| Secrets baked into the image                                          | Distributed to every node that pulls it                               | Environment variables on the container group                           |
| Ignoring `137`                                                        | Misread as OOM when it was a requested reallocate or restart          | Check System Events; raise memory only if no IMDS action was requested |

## Symptom → cause → fix

| Symptom                                                                             | Likely cause                                                                       | Fix                                                                             |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Loops between `downloading` and `allocating`                                        | Process exits immediately                                                          | Check System Events exit code; add a foreground process                         |
| `StartFailure:-1`                                                                   | Bad entrypoint/command, wrong arch, GPU runtime mismatch                           | Run the exact command locally; check arch and CUDA/ROCm vs class                |
| Never `running`; instances move from node to node; logs stop at "Instance Starting" | The command cannot run: missing program, `sleep infinity` on BusyBox, shell syntax | Run the exact command array locally and fix it                                  |
| Stuck `downloading` beyond about 2 min/GB                                           | Slow node or oversized image                                                       | Reallocate the instance; shrink the image                                       |
| Group `pending` a long time, nothing logged yet                                     | The image is still being pulled: a large image or a busy platform                  | Wait; shrink the image; contact support if it lasts very long                   |
| Gateway 503 while the group is `running`                                            | IPv4-only bind, wrong port, readiness not passing, or ready under a minute ago     | Bind `::`; match `networking.port`; check each instance's READY; wait a minute  |
| Gateway 524                                                                         | The response took longer than 100 seconds                                          | Stream the response, or use a job queue                                         |
| Gateway 403                                                                         | Auth on, key missing/wrong; or brief route-table delay                             | Send `Salad-Api-Key`; wait a few minutes; contact support if persistent         |
| `Exited:137` with no OOM in logs                                                    | Requested reallocate/restart, or memory limit                                      | Check System Events before raising memory                                       |
| Works on first instance, breaks after reallocation                                  | State on local disk or in memory only                                              | Externalize state; make startup idempotent                                      |
| Queue jobs stay `pending` while the group runs                                      | The image does not run the worker, or the worker died                              | Run and supervise the worker; read the container logs at `SALAD_LOG_LEVEL=info` |
| A new instance's first jobs fail within seconds (`connection refused`)              | The worker started before the app listened                                         | Gate the worker on the app (step 8)                                             |
| Job `failed` after four quick attempts, no reason given                             | The app answered non-2xx, or the response was over 10 MB                           | Log failures in the app; keep responses under 10 MB                             |
| Jobs never reach the app's handler                                                  | Queue connection port or path does not match the app's route                       | Align them, path with a leading slash; supervise both processes                 |
| A job reads `running` for minutes                                                   | Its instance was interrupted, or its group stopped                                 | Expect a retry after about 5.5 minutes; make handlers idempotent                |
| App output missing from the logs                                                    | Logging to a file, or the first line after a restart                               | Log to stdout and stderr                                                        |

## Safety, verification, escalation

- Building an image needs no SaladCloud credentials; never place API keys, registry passwords, or tokens in a
  Dockerfile, image layer, container command, or committed file. Refer to them by environment variable name. Testing on
  SaladCloud creates a billed container group: confirm with the user first, and delete it when done.
- Do not remove or weaken a user's existing probes, resource limits, or authentication to make a deployment "work";
  explain the trade-off and stop for their decision. Removing probes for a by-hand debugging session is the exception,
  and they go back before the real deployment.
- Verify claims about the live platform (GPU classes, prices, quota, current instance state) with the preflight skill
  and current API reads rather than from this document.
- Success is the image starting with the group's exact command, answering on IPv6 at the configured port, passing the
  probes as designed, and surviving a kill-and-restart without losing committed work; for a queue worker, also taking no
  job before the app answers.
- When a container fails in a way this skill does not explain, load `salad-container-engine-troubleshoot`, which builds
  the evidence package for [SaladCloud support](/support). Retry image pulls and starts only through the platform's own
  restart and reallocation; do not script rapid redeploy loops.
