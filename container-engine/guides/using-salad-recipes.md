---
title: "Using Salad Recipes"
slug: "using-salad-recipes"
excerpt: ""
hidden: false
createdAt: "Thu Oct 19 2023 10:52:21 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Thu Mar 21 2024 15:50:51 GMT+0000 (Coordinated Universal Time)"
---
Recipes offer the simplest way to launch applications on Salad Cloud.  Recipes allow you to run the most popular models, without having to worry about the underlying infrastructure.  The recipes we offer in our verified library are pre-made containers for you to run on Salad.  These containers come pre-configured with all the necessary settings and dependencies for a particular model.  Recipes offer a quick and convenient solution to deploy popular models and start serving inference via an API.  

We recommend getting started with Recipes if you’re looking to test Salad, or if you’re running small-scale inference and don’t need a high level of customization. If you’re done with testing, or you’re looking to run your own custom images right away, we recommend checking out SCE and deploying your own containers.

In this step-by-step guide, we will walk you through the process of deploying a recipe using the Salad Cloud Portal. Let's get started!

### Step 1: Login to the Salad Cloud Portal

1. Open your preferred web browser and navigate to the [Salad Cloud Portal](https://portal.salad.com/).
2. Enter your login credentials (username and password) to access your account dashboard.  Navigate to your desired organization and project within the portal.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/c7f45e8-image.png",
        null,
        "Login Page"
      ],
      "align": "center",
      "caption": "Login Page"
    }
  ]
}
[/block]


### Step 2: Add Billing Information

1. Go ahead and add your billing information by selecting “Billing” on the left-hand side menu. Billing information is required to deploy any image on Salad, be it a Recipe or custom. Receive an additional $25 in free credit by adding billing information and prepaying $50. Additional information regarding billing can be found on [this page](https://docs.salad.com/docs/billing).

### Step 3: Deploy a New Recipe

1. Locate the "Recipe Deployment" option in the right tab of the portal interface and click on it.
2. Click on the "Deploy a New Recipe" option.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/e79f0ba-image.png",
        null,
        "Recipe Deployment Page"
      ],
      "align": "center",
      "border": true,
      "caption": "Recipe Deployment Page"
    }
  ]
}
[/block]


3. You will then see a list of all the available recipes on the Salad Portal. Select the recipe corresponding to your desired model. In this example, we are using the "Llama - 7B" model.  We add to and update our Recipes Marketplace regularly,  to include the most popular models.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/b2593ea-image.png",
        null,
        "Recipe Selection"
      ],
      "align": "center",
      "border": true,
      "caption": "Recipe Selection"
    }
  ]
}
[/block]


4. After selecting the model, you will be provided with detailed information related to that model. This information includes "How to Use," "Intended Uses & Limitations," "Hardware Requirements," and "Reference."  You will also see the associated cost for running the model (per-replica).  
5. Finally, click on the "Configure & Deploy" button to proceed with the deployment of the selected recipe.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/8201d10-image.png",
        null,
        "Recipe Description"
      ],
      "align": "center",
      "border": true,
      "caption": "Recipe Description"
    }
  ]
}
[/block]


### Step 4: Configure and Deploy a Recipe

Once you've chosen the recipe you want to deploy, follow these steps:

1. Configure the name for your deployment.
2. Set the replica count (from 1 to 100).  We recommend you deploy with 2+ replicas to ensure the uptime of your deployment.  If you run into quota limitations, contact our team via the provided link to request a quota increase. 

_Note: You can change the recipe on this page if necessary._

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/eacf28c-image.png",
        null,
        "Configure Recipe"
      ],
      "align": "center",
      "border": true,
      "caption": "Configure Recipe"
    }
  ]
}
[/block]


### Step 5: Start the Container Group

After the deployment is successful, navigate to the container configuration page. You will see the details of your configured container. Click the "Start" button to initiate the container and push it into a running state.  Learn more about [the deployment lifecycle here](https://docs.salad.com/docs/deployment-lifecycle).  

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/cb1d587-image.png",
        null,
        "Start the container"
      ],
      "align": "center",
      "border": true,
      "caption": "Start the container"
    }
  ]
}
[/block]


### Step 6: Use your Recipes

Now that you’ve deployed your Recipe, you’ll see a dashboard with the API URL for your Recipe, as well as the status of the nodes running your instances.  
_Note: It can sometimes take some time even after a node has reached the "running" state for the recipe deployment to be ready to serve inference, as it may still be downloading or starting up the mode._

Instructions on how to use any of the models can be found on the Recipe card itself, which you can also find on the Deployment Details tab of the deployment dashboard. Interacting with most recipes is done via an API at the Access Domain provided on the deployment dashboard.

Whenever you’re interacting with a Recipe deployment, you’ll also need your API token which can be found by clicking on your profile at the top right, and selecting API Access. Include your API key as a header in the format Salad-Api-Key: {API_KEY}.

For this example, you’ll be submitting this POST request to your URL, using the API key as described above:

```json
{
  "prompt": "cat",
  "batch_size": 1,
  "steps": 35,
  "refiner_start": 20,
  "denoising_strength": 0.43,
  "cfg_scale": 7,
  "width": 1216,
  "height": 896,
  "send_images": true,
  "save_images": false,
  "enable_hr": true,
  "hr_second_pass_steps": 35,
  "hr_upscaler": "None"
}
```

Once your inference is completed, you’ll receive a response to the request containing the base64 to decode for your image.

```json
{
  "images": "string[]",
  "parameters": "Text2ImageRequest",
  "info": "string"
}
```