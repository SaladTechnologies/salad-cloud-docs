---
title: "Managing Deployments"
---

### Listing your Container Deployments

In the Salad Cloud Portal, you're able to see your deployments for each project on the Container Deployments List page. This page shows a high-level view for each of the container groups within the project, including:

- Name of the deployment
- Date created
- [Deployment status (Preparing, Stopped, Deploying, Running, Failed)](https://docs.salad.com/docs/deployment-lifecycle)
- Replicas running
- Version
- Container Gateway details (if enabled)
- Image source
- Allocated resources (total desired replica count and vCPUs, RAM and GPU(s) allocated to each replica)

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/5ef427e-image.png",
null,
"The Container Deployments List page."
],
"align": "center",
"border": true,
"caption": "The Container Deployments List page."
}
]
}
[/block]

<br>

### Managing a Container Deployment

Click on any of your deployments to drill down to the Container Deployment Detail page. From here, you can start, stop, and delete your deployment, as well as edit the display name, replica count, image source, resource requirements, and other configuration settings

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/92a596a-image.png",
null,
"The Container Deployment Detail Page"
],
"align": "center",
"border": true,
"caption": "The Container Deployment Detail Page"
}
]
}
[/block]

<br>

### Managing Container Instances

On this page, you can also see a table of all instances of your container that have been allocated, are running, stopping, or failed. You can also manage these instances by clicking the action button next to an entry in the list of running instances.

You can perform the following actions:

** Restart a container instance** Occasionally, a workload may run for awhile on your node and then some part of the application might hang. In these cases, it's typically faster to get back up and running by restarting the container on the same node, rather than searching for a new one. The **Restart** option allows you to restart your container on the node, with all settings and downloaded data intact.

** Recreate a container instance** For a harder reset, the **Recreate** option allows you to rebuild the container from scratch on the node. These features are accessible from the actions dropdown next to each node on the container group detail page.

**Reallocate a container instance** If a workload fails to run, Salad will automatically reallocate your container to a new node that matches the requirements you specified. However, in some rare cases, a node has trouble running a container replica but doesn't outright _fail_. If this happens, it's helpful to be able to manually trigger a reallocation of the workload to a new node.

** View Container Logs** Use this link to open the Container Logs tab with the Machine ID filter pre-filled.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/71f721a-image.png",
null,
"Restart, recreate, reallocate, and view container logs."
],
"align": "center",
"border": true,
"caption": "Restart, recreate, reallocate, and view container logs."
}
]
}
[/block]

<br>

### Failures

If container images exit with a 0 exit code, they may be restarted on the same node. If container images exit with a non-0 exit code, they will be blocked from the current node and reallocated to another node. Customization of this behavior is coming soon.

### Editing Your Container Group Deployment

Inside the "Edit" option on the Managing Deployments page in Salad, you have the flexibility to modify key parameters of your Container Group deployment.

- You can change the Display Name to make deployments more descriptive and easily identifiable. Note: the Container Group Name, set upon creation, cannot be edited.
- You can update the Image Source URL. For private registries, re-enter authentication details. You'll see the first 12 characters of the image digest hash after saving.
- You can adjust the replica count to scale your application up or down as needed.
- You can modify hardware resource requirements, such as the number of vCPUs, Memory (RAM), GPUs, and [Disk Space](https://docs.salad.com/docs/disk-space).
- You can edit the [Health Check Probes](https://docs.salad.com/docs/health-probes) (Startup, and Liveness).
- You can edit the [Command](https://docs.salad.com/docs/specifying-a-command).
- If enabled, you can edit the [Container Gateway](https://docs.salad.com/docs/networking) Port. Note: the edit Container Group functionality doesn't allow for the Container Gateway to be disabled, enabled, or authentication to be changed.
- You can modify or enable/disable the [External Logging](https://docs.salad.com/docs/external-logging) Services.
- You can edit the [Environment Variables](https://docs.salad.com/docs/environment-variables).

This editing functionality lets you update your container images, change hardware requirements, adjust configuration aspects, and utilize new features that Salad may release. Changes to your Container Groups can be made with minimal downtime and while retaining the original Container Gateway configuration (DNS name). As you make changes, you will see the predicted cost associated with those choices updated in real-time.

If you are updating the Image Source, you will not be able to make additional edits until the new image is done preparing / pulling. To avoid confusion the “Edit” button will be disabled until this process is complete.

If you update just the display name and/or replica count, the Container Group won't be assigned a new version. However, if you update other variables, it will. The instances currently running will continue to run the version of the Container Group that they were started with. Any new instance or an instance that gets a new node assigned to it, will start running with the new Container Group version. To manually update an instance to run the updated version, Reallocate the instance. Using this option will assign a new node to the instance and build the container from scratch. In the case that a node no longer meets the new hardware resource requirements, the Salad system will reallocate it within a period of 5 minutes or less.

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/271b376-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]

[block:image]
{
"images": [
{
"image": [
"https://files.readme.io/7bd5e3f-image.png",
null,
""
],
"align": "center",
"border": true
}
]
}
[/block]

<br>

To access the editing options for your Container Group deployment, simply navigate to the Salad dashboard, locate your deployment, and select the "Edit" option. To access the Reallocate option after edits resulting in a new container version, locate the container instance (on the Container Group detail page) expand the menu in the Actions column, and select "Reallocate".
