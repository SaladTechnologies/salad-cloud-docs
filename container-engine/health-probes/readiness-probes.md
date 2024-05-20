---
title: "Readiness Probes (Coming Soon)"
---

# Overview

Readiness probes are only available if [Container Gateway](https://docs.salad.com/docs/networking) is turned on. They run after the startup probe has completed successfully. They are typically used to evaluate whether the application running in your container is ready to accept traffic. If configured, no traffic will be sent from the load balancer until the readiness probe has passed, so prevent your readiness probe from passing until you have downloaded and warmed up your models. Readiness probes can flap back between passing and failing. If a container's readiness probe reaches the failure state, the container will continue to run on the node but the load balancer will not route any networking traffic. Readiness probe configuration should be fairly strict in order to get that signal out as fast as possible so requests get routed to other nodes.

<br />

## Successful Readiness Probe

![](https://files.readme.io/bca39c9-image.png)

<br />

## Failed Readiness Probe

![](https://files.readme.io/2a724dc-image.png)

<br />

# Configuration

Check the checkbox to enable the readiness probe. Currently, the supported protocols are `exec`, `gRPC`, `TCP`, and `HTTP/1.X`

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/1a0226c-image.png",
null,
""
],
"align": "center",
"sizing": "300px",
"border": true
}
]
}
[/block]

<br />

# Probe Status

You can see the status of a readiness probe, if configured, on each instance of a container group.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/43b86cb-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]
