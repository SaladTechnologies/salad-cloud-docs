---
title: "Run TGI (Text Generation Interface) by Hugging Face"
slug: "run-tgi-text-generation-interface-by-huggingface"
excerpt: ""
hidden: false
createdAt: "Mon Nov 13 2023 19:06:19 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Tue Apr 09 2024 16:06:40 GMT+0000 (Coordinated Universal Time)"
---
TGI (Text Generation Interface) is a toolkit for deploying and service Large Language Models (LLMs). TGI enables high-performance text generation for the most popular open-source LLMs, including Llama, Falcon, StarCoder, BLOOM, GPT-NeoX, and T5.

[Learn More Here](https://huggingface.co/docs/text-generation-inference/main/en/index)

[Github Repo](https://github.com/huggingface/text-generation-inference)

# Deploying TGI on Salad

## Container

Hugging Face provides a pre-built docker available via the Github Container registry. 

```Text Docker
ghcr.io/huggingface/text-generation-inference:1.1.1
```

In order to deploy the container on Salad, you will need to configure the container with your desired models, plus any additional settings. These options can either be configured as part of the `CMD` or can be set as [Environment Variables](doc:environment-variables) when creating your container group. Here is a complete list of [all TGI options](https://huggingface.co/docs/text-generation-inference/main/en/basic_tutorials/launcher)

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/1074d8d-image.png",
        null,
        "Example TGI Options"
      ],
      "align": "center",
      "sizing": "400px",
      "border": true,
      "caption": "Example TGI Options"
    }
  ]
}
[/block]


## Required - Container Gateway Setup

In addition to any options that you need to run the model, you will need to configure TGI to use [IPv6](doc:enabling-ipv6) in order to be compatible with Salad's Container Gateway feature. This is done by simply setting `HOSTNAME` to `::`

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/064f253-image.png",
        null,
        "Salad portal Env Vars"
      ],
      "align": "center",
      "sizing": "400px",
      "border": true,
      "caption": "Salad portal Env Vars"
    }
  ]
}
[/block]


## Recommended - Health Probes

[Health Probes](doc:health-probes) help ensure that your container only serves traffic it is ready and ensures that the container continues to run as expected. When the TGI container starts up, it begins to download the specific model before it can start serving requests. While the model is downloading, the API is unavailable. The simplest health probe is to check the `/health` endpoint. If the endpoint is running, then the model is ready to serve traffic.

### Exec Health Probe

The `exec` health probe will run the given command inside the container, if the command returns an exit code of 0, the container is considered in a healthy state. Any other exit codes indicate the container is not ready yet. 

The TGI container does not include `curl` or `wget` so in order to check the `:80/health` API we decided to use python's requests to check the API. 

```Text bin
python -c "import requests,sys;sys.exit(0 if requests.get('http://localhost:80/health').status_code == 200 else -1)"
```

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/e851b39-image.png",
        null,
        ""
      ],
      "align": "center",
      "sizing": "4px"
    }
  ]
}
[/block]


### Http Health Probe - Coming Soon