---
title: "Liveness Probes"
---

# Overview

Liveness probes are similar to startup probes, except that they run after the startup probe has completed successfully. Typically, Liveness probes are used to evaluate whether the application running in your container is in a healthy state. If a container's liveness probe reaches the failure state, the container will be reallocated to a different node. Liveness probes are a good place to put logic that checks for CUDA errors, and other unrecoverable states.

## Successful Liveness Probe

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/67f4869-Liveness_Recovers.png",
"",
""
],
"align": "center"
}
]
}
[/block]

## Failed Liveness Probe

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/05e66d5-Liveness_Failure.png",
"",
""
],
"align": "center"
}
]
}
[/block]

# Configuration

Check the checkbox to enable the liveness probe. Currently, the supported protocols are `exec`, `gRPC`, `TCP`, and `HTTP/1.X`

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/d7a0dfb-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]
