---
title: "Deploy via portal"
slug: "deploy-via-portal"
excerpt: ""
hidden: true
metadata: 
  image: []
  robots: "index"
createdAt: "Thu Feb 09 2023 04:41:39 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Fri Oct 20 2023 07:49:20 GMT+0000 (Coordinated Universal Time)"
---
## **Here are steps to deploy your container using salad portal: **

If this is your first time, be sure to sign up and register here **<https://portal.salad.com>** or follow the guide** [here](https://docs.salad.com/docs/register-on-salad-portal)** to setup your salad portal account 

- ** Go to <http://portal.salad.com> and "Create Organization"** 

![](https://files.readme.io/0dec642-KbLJL6xfYl.png "KbLJL6xfYl.png")

- ** Select the Created Organisation.**  
  We are using **"Salad Technologies"** 

![](https://files.readme.io/dcb0f16-rqCWWc9eMV.png "rqCWWc9eMV.png")

- **Create New Project** 

![](https://files.readme.io/8e6b337-ZcmAxga60F.png "ZcmAxga60F.png")

- **Select Project "Demo"** 

![](https://files.readme.io/d02a76c-NvIAZpTgp4.png "NvIAZpTgp4.png")

- **Create New Container Group** 

![](https://files.readme.io/1640c95-iFLWVSvdZn.png "iFLWVSvdZn.png")

- **Select "Public" and give the container a preferable name e.g. test** 

![](https://files.readme.io/058ba22-5OnTZ7yaCi.png "5OnTZ7yaCi.png")

- **Copy your Container image tag.**

Your image URL  tag should be in this format **docker.io/example-org/my-image:latest** :  
This is a reference to a Docker Container  image . 

Here we are using an already existing image **docker.io/heygordian/node-app:latest ** and click on "Next Container Resources"

![](https://files.readme.io/d876461-hMC7YOW3Pd.png "hMC7YOW3Pd.png")

- **Select Review & Deploy** 

![](https://files.readme.io/5b9c1a6-FuXuykEx3o.png "FuXuykEx3o.png")

- **Deploy Container Groups** 

![](https://files.readme.io/66c2ec7-AbHXzGKihs.png "AbHXzGKihs.png")

- **Congratulations! Your Container is now running on Salad Portal** 

![](https://files.readme.io/8d8ccfc-u7h6J7yTel.png "u7h6J7yTel.png")

- **Review and see the status of your Container which is successfully "Running"**

![](https://files.readme.io/6e08ac7-6boPTdQwZP.png "6boPTdQwZP.png")

**Note:** 

- There currently a max **image size of 10 GB (note: this may change)**
- We pull and store images at moment of container group creation, so if the image is modified they will have to create a new container group

**Status of container groups with private images**

- While the image is being pulled and stored, the container group status will be pending
- Once the image is ready, the container group status will change to stopped, and the container group can be started.

**Failures**  
A few unique failures can occur with container images stored on private registries

- Failure to authenticate: This will occur if we are unable to authenticate to the private registry with the credentials provided. Double check the credentials are correct and try again.
- Failure to store: This will occur if we are unable to store the container image. This should be a temporary condition so try again.
- Image too large: This will occur if the container image is too large. You will need to use a smaller container image.

If issues persist, **[please contact support here. ](mailto:cloud@salad.com) **