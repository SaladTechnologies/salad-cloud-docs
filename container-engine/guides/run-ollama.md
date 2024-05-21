---
title: "Run Ollama"
slug: "run-ollama"
excerpt: ""
hidden: false
createdAt: "Thu Mar 14 2024 20:18:43 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Tue Apr 09 2024 16:05:43 GMT+0000 (Coordinated Universal Time)"
---
Ollama is a toolkit for deploying and service Large Language Models (LLMs). Ollama enables local operation of open-source large language models like Llama 2, simplifying setup and configuration, including GPU usage, and providing a library of supported models.

[Learn More Here](https://ollama.com/)

## Ollama API

Ollama can be used as an API that can:

- Generate text completions using different language models and tags.
- Stream responses in JSON format or receive them as single objects.
- Include optional parameters such as images, formatting options, and system messages.
- Maintain conversational memory using the context parameter.
- Control response streaming and model memory retention.

For detailed instructions and examples, refer to the Ollama documentation: <https://github.com/ollama/ollama/blob/main/docs/api.md>

# Deploying Ollama on Salad

## Container

Ollama provides a pre-built docker available via the Docker Container registry : <https://hub.docker.com/r/ollama/ollama>

In order to deploy the container on Salad, you will need to specify the image: 

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/a48be4d-image.png",
        null,
        ""
      ],
      "align": "center",
      "border": true
    }
  ]
}
[/block]


All the other options can be specified using api requests. 

## Required -  Container Gateway Setup

In addition you need to specify the port your api will be available through. Default port for Ollama is 11434

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/af91390-image.png",
        null,
        ""
      ],
      "align": "center",
      "border": true
    }
  ]
}
[/block]
