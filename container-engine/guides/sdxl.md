---
title: "SDXL"
slug: "sdxl"
excerpt: ""
hidden: false
createdAt: "Tue Dec 12 2023 17:06:04 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Tue Apr 09 2024 16:26:24 GMT+0000 (Coordinated Universal Time)"
---
# sdnext-dynamic

This wraps our SDNext image with an entrypoint script that downloads a checkpoint at runtime based on an environment variable.

You can use the prebuilt docker image at:

```
saladtechnologies/sdnext:dynamic
```

The Github Repo is available here: <https://github.com/SaladTechnologies/sdnext-dynamic>

### "Baked" Images

If you want an image with the model preloaded, you can use one of the "baked" images. These are built with the `build-baked` script, and will not need to download the models at runtime.

- `saladtechnologies/sdnext:sdxl1.0` - Preloaded with SDXL [Base](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) and [Refiner](https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0)
- `saladtechnologies/sdnext:dreamshaper8` - Preloaded with [DreamShaper 8](https://civitai.com/models/4384?modelVersionId=128713)
- `saladtechnologies/sdnext:rundiffusionxl-beta` - Preloaded with [RunDiffusion XL Beta](https://civitai.com/models/120964?modelVersionId=131579) and [SDXL Refiner](https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0)
- `saladtechnologies/sdnext:dreamshaper8-qr-code` - Preloaded with [DreamShaper 8](https://civitai.com/models/4384?modelVersionId=128713) and [QR Code Monster](https://civitai.com/models/111006?modelVersionId=122143)

## Build your own image

### Without a model preloaded

The "baked" images use this one as a base

```shell
## Usage: ./build [--push]
./scripts/build
```

### With a model preloaded

```
Usage: ./build-baked [OPTIONS]

Options:
  --push                          Push the built image to DockerHub. Default: false
  --civitai-version-ids <v1,v2>   Comma-separated list of CivitAI model version IDs to load. Default: ""
  --load-refiner                  Load the refiner model. Default: false
  --load-sdxl-base                Load the SDXL base model. Default: false
  --controlnet-urls <url1,url2>   Comma-separated list of ControlNet download URLs. Default: ""
  --extension-urls <url1,url2>    Comma-separated list of extension Git URLs. Default: ""
  --ckpt-urls <url1,url2>         Comma-separated list of CKPT download URLs. Default: ""
  --vae-urls <url1,url2>          Comma-separated list of VAE download URLs. Default: ""
  --lora-urls <url1,url2>         Comma-separated list of LoRa download URLs. Default: ""
  --tag <tag>                     Tag to use for the image. Defaults to the CivitAI version IDs with a hyphen between them
  --image <image>                 Image to build. Default: saladtechnologies/sdnext
  --help                          Show this message and exit
```

**Examples**

Load 2 models from civitai

```shell
./scripts/build-baked --civitai-version-ids 122143,128713
```

Load SDXL Base and Refiner, and push the image to your own repository with a custom tag

```shell
./scripts/build-baked --load-sdxl-base --load-refiner --push --tag sdxl1.0 --image my-org/my-repo
```

### Original SDXL + Refiner

```shell
./scripts/build-sdxl
```

## Environment Variables

| Variable                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Default |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| HOST                      | The host to listen on. Use `[::]` on Salad. You may need to use an ipv4 address like `0.0.0.0` for local development                                                                                                                                                                                                                                                                                                                                                                             | `[::]`  |
| PORT                      | The port to listen on. This should match the port you configure for Salad networking.                                                                                                                                                                                                                                                                                                                                                                                                            | 7860    |
| CIVITAI_MODEL_VERSION_IDS | A comma-separated list of model version IDs to download. ex `128713` for just [Dreamshaper 8](https://civitai.com/models/4384?modelVersionId=128713) or `128713,166808` for Dreamshaper and [Arterior](https://civitai.com/models/112229/arterior-digital-art-style). This supports Checkpoints, VAEs, Controlnets, and LoRAs. The rightmost checkpoint value will be the default checkpoint when the server starts, and the rightmost vae value will be the default vae when the server starts. | None    |
| LOAD_SDXL_BASE            | If set to `1`, the SDXL base model will be downloaded.                                                                                                                                                                                                                                                                                                                                                                                                                                           | 0       |
| LOAD_REFINER              | If set to `1`, the SDXL refiner model will be downloaded.                                                                                                                                                                                                                                                                                                                                                                                                                                        | 0       |
| CONTROLNET_URLS           | A comma-separated list of download urls for controlnets. ex `https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_canny_mid.safetensors?download=true`                                                                                                                                                                                                                                                                                                              | None    |
| CLI_ARGS                  | Additional arguments to pass to the `sdnext` launch command. Options can be found with `--help`                                                                                                                                                                                                                                                                                                                                                                                                  | None    |
| EXTENSION_URLS            | A comma separated list of extension git urls to load. e.g. `https://github.com/deforum-art/sd-webui-deforum`                                                                                                                                                                                                                                                                                                                                                                                     | None    |
| CKPT_URLS                 | A comma separated list of checkpoint download urls to load. e.g. `https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors?download=true`                                                                                                                                                                                                                                                                                                         | None    |
| VAE_URLS                  | A comma separated list of vae download urls to load. e.g. `https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/diffusion_pytorch_model.safetensors?download=true`                                                                                                                                                                                                                                                                                                                  | None    |
| LORA_URLS                 | A comma separated list of lora download urls to load. e.g. `https://huggingface.co/ostris/ikea-instructions-lora-sdxl/resolve/main/ikea_instructions_xl_v1_5.safetensors?download=true`                                                                                                                                                                                                                                                                                                          | None    |

## Built-in Exec Probes

An exec probe is a command that is run periodically to check the health or readiness of the container. It returns a zero exit code if the container is healthy, and a non-zero exit code if the container is unhealthy. You can configure the maximum number of retries and the interval between retries using either the portal or the [Create Container Group API](https://docs.salad.com/reference/create_container_group). Learn more about health probes in [the docs](https://docs.salad.com/docs/health-probes).

### Startup Probe

This probe will return a zero exit code when the server is ready to accept connections. It will return a non-zero exit code if the server is not ready to accept connections.  Keep in mind it can take quite a while to download the models, so be sure to set a generous number of retries and a long interval, or your container will never start taking traffic, and will be continually reallocated.

For example, SDXL takes quite a while to load the model, and one of the things the startup probe does is enable the refiner (if you've configured the container to do so). Enabling the refiner can take up to 3 minutes in rare circumstances, so the maximum timeout should be at least 180 seconds. The total time required to reach readiness could be quite long, so we want to make sure the failure threshold allows for enough time. In this case, I've set it to 600, which combined with the period, gives us 600 seconds (10 minutes) for the container to come up. For a container using an SD 1.5 model, you could get away with considerably shorter timeouts and failure thresholds. You will want to experiment with your specific model(s) to find the right values.

**Portal**

- **Protocol**: `exec`
- **Command**: Command: `python` , Arg: `/probes/readiness.py`
- **Initial Delay Seconds**: 20
- **Period Seconds**: 1
- **Timeout Seconds**: 200
- **Success Threshold**: 1
- **Failure Threshold**: 600

**API**

```json
{
  "exec": {
    "command": [
      "python",
      "/probes/readiness.py"
    ]
  },
  "initial_delay_seconds": 20,
  "period_seconds": 1,
  "timeout_seconds": 200,
  "success_threshold": 1,
  "failure_threshold": 600
}
```

### Liveness Probe

This probe will return a zero exit code when the server has not encountered any memory problems. It will return a non-zero exit code if the server has run out of, or is about to run out of, memory.

Since this probe primarily checks for memory issues, it should be configured with a short timeout and a low failure threshold. If the container is running out of memory, it will likely not be able to recover, so we want to fail fast and let the container be reallocated.

**Portal**

- **Protocol**: `exec`
- **Command**: Command: `python` , Arg: `/probes/healthcheck.py`
- **Initial Delay Seconds**: 600
- **Period Seconds**: 30
- **Timeout Seconds**: 2
- **Success Threshold**: 1
- **Failure Threshold**: 3

**API**

```json
 {
  "exec": {
    "command": [
      "python",
      "/probes/healthcheck.py"
    ]
  },
  "initial_delay_seconds": 600,
  "period_seconds": 30,
  "timeout_seconds": 2,
  "success_threshold": 1,
  "failure_threshold": 3
}
```

## Finding Your Model Version ID (Website)

1. Navigate to the Civit.ai page for the model you want to use

   [block:image]{"images":[{"image":["https://files.readme.io/376ada9-image11.png","",""],"align":"center"}]}[/block]

2. Click the version of the model you want to download

   [block:image]{"images":[{"image":["https://files.readme.io/f24d4f4-image21.png","",""],"align":"center"}]}[/block]

3. Copy the version ID from the URL

   [block:image]{"images":[{"image":["https://files.readme.io/bb4c717-image31.png","",""],"align":"center"}]}[/block]

**OR**

2. Copy the link from the download button  
   ![](https://files.readme.io/2ecae2c-image51.png)

3. Paste the link into a text editor and copy the model version ID from the URL

```
https://civitai.com/api/download/models/128713
```

For this url, the model version id is `128713`.

## Finding Your Model Version ID (API)

1. Navigate to the Civit.ai page for the model you want to use  
   ![](https://files.readme.io/0522c19-image11.png)

2. Grab the model ID from the URL  
   ![](https://files.readme.io/7fcd140-image41.png)

3. Use the API to get the model versions

```shell
curl  -X GET \
  'https://civitai.com/api/v1/models/4384'
```

You'll get a JSON response that includes a `.modelVersions` field:

```
"modelVersions": [
    {
      "id": 128713,
      "modelId": 4384,
      "name": "8",
      "createdAt": "2023-07-29T15:56:46.392Z",
      "updatedAt": "2023-08-01T13:38:21.400Z",
      "trainedWords": [],
      "trainingStatus": null,
      "trainingDetails": null,
      "baseModel": "SD 1.5",
      "baseModelType": "Standard",
      "earlyAccessTimeFrame": 0,
      "description": "<ul><li><p>Better at handling Character LoRA</p></li><li><p>Better at photorealism without sacrificing range (can still do art and anime pretty well, even if you might have to increase weight)</p></li><li><p>Better at NSFW</p></li></ul>",
      "vaeId": null,
      "stats": {
        "downloadCount": 157806,
        "ratingCount": 673,
        "rating": 4.9
      },
      "files": []
      ...
    }
]
```

Find the model version you want to use and copy the `id` field.

## Deploying on Salad (Portal)

As an example, we're going to deploy the Dreamshaper XL model

### Create a Deployment

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/c987955-setup11.png",
        null,
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


1. Name your deployment
2. Select the `saladtechnologies/sdnext:dynamic` image
3. Select how many vCPUs you need. For this we'll use 2
4. Select how much RAM you need. Since we plan on using the refiner model, we'll use 30GB

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/799dedc-setup21.png",
        null,
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


5. Select your GPUs. For an SDXL based model, we'll want GPUs with at least 16GB of VRAM.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/71b63f5-setup31.png",
        null,
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


6. Click "edit" on the Container Gateway section, and enable networking for port 7860 (the default port for SDNext).

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/2fc613c-image.png",
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


7. Click "edit" on the Environment Variables section, and add the following variables:
   - `HOST` with a value of `[::]`
   - `CIVITAI_MODEL_VERSION_IDS` with a value of `126688`
   - `LOAD_REFINER` with a value of `1`

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/b22f861-setup51.png",
        null,
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


8. Click "Deploy" to finish creating your deployment. Then, click "Start" to start it.

### Your Finished Deployment

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/13ae364-deployment-info1.png",
        null,
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


With the environment configured like this:

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/8e30503-deployed-env1.png",
        null,
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]
