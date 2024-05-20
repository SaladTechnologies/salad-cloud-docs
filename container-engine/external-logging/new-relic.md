---
title: "New Relic"
---

[New Relic](https://newrelic.com/) is a popular observability platform that you can get started with for free.

To connect your Salad Container Group to New Relic, you'll need 2 pieces of information:

1. Host: This refers to which New Relic endpoint to send your logs to. There are two options:
   1. <https://log-api.newrelic.com/log/v1> - Use this if you have elected to have your data hosted in New Relic's NA data center.
   2. <https://log-api.eu.newrelic.com/log/v1> - Use this if you have elected to have your data hosted in New Relic's EU data center.
2. Ingestion Key: This is long random string used to securely connect your Salad containers to New Relic.  
   You can find this key by clicking your name in the lower left hand corner of the screen (1). This opens a menu, where you will see an option for "API Keys"(2)

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/afefcb5-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]

From there, identify the key named "Installer Ingest License Key" (1). Open the `...` menu on the right-hand side of that row (2), and select "Copy Key" from the menu (3). This copies the key value to your clipboard.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/25a68b6-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]

Armed with this information, you're ready to set up your Container Group in Salad. On the "Create Container Group" page in the [portal](https://portal.salad.com), find the "External Logging Services" options.

![](https://files.readme.io/3772ffc-image.png)

Select "New Relic" from the "Select a Container Logging Service" menu. Fill in the fields with the information gathered above, and hit the "Configure" button at the bottom.

![](https://files.readme.io/a023a46-image.png)

Finish setting up the rest of your container group settings, and deploy it! Once your container is running and logging something, those logs will start appearing in the logging panel of New Relic

![](https://files.readme.io/ea8a40e-image.png)
