---
title: "Startup Probes"
---

# Overview

Startup probes, when configured, run as soon as the container is created. They are typically used to ensure that the application has started, and is ready to accept traffic. No traffic will be sent from the load balancer until the startup probe has passed, so prevent your startup probe from passing until you have downloaded and warmed up your models.

## Successful Startup Probe

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/c651b89-Startup_Success.png",
"",
""
],
"align": "center"
}
]
}
[/block]

## Failed Startup Probe

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/1046446-Startup_Failure.png",
"",
""
],
"align": "center"
}
]
}
[/block]

# Configuration

Check the checkbox to enable the startup probe. Currently, the supported protocols are `exec`, `gRPC`, `TCP`, and `HTTP/1.X`

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/bff4e47-image.png",
null,
""
],
"align": "center",
"sizing": "400px",
"border": true
}
]
}
[/block]

> 📘 Tips for slow-starting containers
>
> SCE attempts to estimate the maximum time the probe can run before resulting in a failure, based on the values in the fields above. This guidance is provided below the Configure button. If you expect your container often takes longer than this to start, you should adjust the thresholds in the fields above to ensure that you're not prematurely reallocating containers that could have reached a successful status.
