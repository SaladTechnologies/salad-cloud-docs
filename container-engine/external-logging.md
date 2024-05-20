---
title: "External Logging"
---

You may wish to stream event logs from your container group deployment to an external service for easier parsing, retention, and monitoring. To configure external logging, click 'edit' on the External Logging Services section on the Container Group Deployment page.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/aa011bd-image.png",
null,
""
],
"align": "center",
"sizing": "450px",
"border": true
}
]
}
[/block]

In the sidebar that appears, select the logging service you wish to use.

> ❓ Logging service not supported?
>
> We're working to expand the logging services supported on SaladCloud. If you're using an external logging service not listed here, please [get in touch](mailto:cloud@salad.com)!
>
> Under the hood, Salad Cloud uses [Fluent Bit](https://docs.fluentbit.io/manual/pipeline/outputs) to collect and send container logs. Check the Fluent Bit documentation here to see if your preferred logging service is supported out of the box. If so, we can easily add support for it - just let us know.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/a2a3a75-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]

Finally, fill out the form fields and press Configure.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/d8a6ecb-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]

> 📘 Don't have an external logging provider?
>
> Check out the [Container Logs](https://docs.salad.com/docs/container-logs) feature in the Salad Portal.
