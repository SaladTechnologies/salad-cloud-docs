---
title: "How to deploy a Node App on Salad"
slug: "how-to-deploy-a-node-app-on-salad"
excerpt: ""
hidden: true
metadata: 
  image: []
  robots: "index"
createdAt: "Mon Dec 26 2022 04:10:35 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Fri Oct 20 2023 07:49:20 GMT+0000 (Coordinated Universal Time)"
---
In this guide, we will build a simple Node.js application, an image, and a container using the image then expose the local host using Cloud flare “Cloudflared” tunnels with free Cloudflare tunnels and deploy on [Salad Container Engine (SCE)](https://docs.salad.com/docs)

## **Prerequisites**

- A Node.js app that you have developed and tested locally
- A [Salad Container Engine(SCE)  account](https://docs.salad.com/docs/register-on-salad-portal)
- Git installed on your local machine

## **How to dockerize a Node.js application**

Before we begin, let’s be sure ** [Docker](https://docs.docker.com/engine/install/) ** and **[Node.js](https://nodejs.org/en/download/package-manager/)** is installed on our system. 

If Docker is not, you can use the links below to download it based on your chosen Operating System (OS) : 

- **[Windows](https://docs.docker.com/docker-for-windows/install/)**
- **[Mac OS](https://docs.docker.com/desktop/install/mac-install/)**
- **[Ubuntu](https://docs.docker.com/engine/installation/linux/ubuntu/)**

To confirm if your **Node.js** has successfully been installed in your machine, open your (CLI tool) command prompt or desired terminal and type this command.  
This will display the version of the installed **`Nodejs`**

**`node  -v`** 

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/1a2fd60-V.PNG",
        "V.PNG",
        625
      ],
      "align": "center",
      "sizing": "smart",
      "caption": "This displays the Nodejs version"
    }
  ]
}
[/block]