---
title: "How to deploy and use Stable Diffusion XL Recipe"
slug: "how-to-deploy-and-use-stable-diffusion-xl-recipe"
excerpt: ""
hidden: false
createdAt: "Tue Apr 02 2024 14:36:47 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Tue Apr 02 2024 17:06:28 GMT+0000 (Coordinated Universal Time)"
---
Using Salad Recipes you can deploy Stable Diffusion XL inference servers with just a few clicks. We offer two variants, an authentication-required API access only version, as well as a Recipe that allows you to connect with no API access token, and that allows for usage of the supplied Graphical UI for testing or personal use.

- Note: When using the GUI version of our Stable Diffusion XL, we recommend deploying to just a single instance, as you’ll only be able to access one at a time via our networking load balancer. Additionally, as this image has no authentication, anyone with access to your Salad URL provided for the deployment will have access to the GUI, so be careful where it’s shared.

<br>

1. Follow the first few steps of our [Using Salad Recipes](https://docs.salad.com/docs/using-salad-recipes) documentation, until you’re signed up and have billing information attached to your account.
2. Once you’re ready, head to the Recipes Marketplace and select the recipe depending on whether you want the API-only, or Graphical UI version.

   - sdnext-stable-diffusion-xl 
   - sd-next-gui-stable-diffusion-xl

   [block:image]{"images":[{"image":["https://files.readme.io/eb2de21-image.png",null,""],"align":"center","border":true}]}[/block]

   <br>
3. Click Configure & Deploy and give your deployment a name, along with how many replicas you want. We recommend at least 2-3 for the API-only version to ensure constant uptime, and 1-2 for the Graphical UI version.
4. Once deployed, wait for your replicas to hit the running state. 

   [block:image]{"images":[{"image":["https://files.readme.io/d6480b1-image.png",null,""],"align":"center","border":true}]}[/block]
5. Once ready, you’ll need the Access Domain Name from the deployment page, along with your API Access Token (If you’re using the API-only version).
   - Whenever you’re interacting with a Recipe deployment, you’ll also need your API token which can be found by clicking on your profile at the top right, and selecting API Access. Include your API key as a header in the format Salad-Api-Key: {API_KEY}. (If you’re using the GUI version, you can skip this.)
6. Next, how you interact with the Recipe will depend on whether you selected the API-only version, or the Graphical UI version.

   - API-only

     - If you’ve selected the API-only version, you’ll be interacting with your recipe by submitting a POST request to the URL provided in the deployment details, which will be your Access Domain Name with some additional URL added to the end.
     - Full information on all the available options are listed on the Recipe Details page, but to make an initial inference we’ll be sending this POST request to the above URL, with your Salad-Api-Key in your header.

       - ```json
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
     - Once you submit the post request, we’ll service it to one of your running replicas and it’ll start generating the image. Once the image is generated, you’ll receive it as a response to your POST request. It’ll look something like this, where the images field is the base64 of your image, ready for you to decode into the JPG/PNG.
       - ```json
         {
           "images": "string[]",
           "parameters": "Text2ImageRequest",
           "info": "string"
         } 
         ```
     - Once you’ve received the response, you can forward your image to its final destination, and you’re ready to send more requests. If you receive a 403 error code when trying to request an image, make sure you’ve added your API key as a header, as this is required. If you’re receiving a 503 error, try waiting a bit longer. It can sometimes take a short period of time for your Recipe to start up fully, even once running on nodes.
   - Graphical UI

     - If you’re instead deploying the Graphical UI version, you won’t need your API key, and instead you’ll be going directly to the Access Domain Name shown on your deployment page.
     - When visiting this URL, you’ll be met by the SD.next GUI to run inference directly in your web browser. The layout is similar to the A1111 interface you may be familiar with already.

   <br>

   [block:image]{"images":[{"image":["https://files.readme.io/ae3dfaf-image.png",null,""],"align":"center","border":true}]}[/block]

   <br>

   - If you’re having issues accessing this page, try adding a / to the end of the URL. If you’re still experiencing issues, try waiting a bit longer. It can sometimes take a short while for the server to start up fully, even once in a running state for the replica node. Please note, that if you’re using the Graphical UI version, you may experience a disconnection if the node serving your replica shuts down or restarts. If you have more than one instance running, you should be able to simply refresh the page and access a new replica node. If you have only one replica, you’ll need to wait until the new node spins up and reaches a running state.