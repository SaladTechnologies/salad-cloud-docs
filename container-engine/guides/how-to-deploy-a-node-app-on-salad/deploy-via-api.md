---
title: "Deploy via API"
slug: "deploy-via-api"
excerpt: ""
hidden: true
metadata: 
  image: []
  robots: "index"
createdAt: "Tue Jan 17 2023 13:17:01 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Fri Oct 20 2023 07:49:20 GMT+0000 (Coordinated Universal Time)"
---
## **Prerequisites**

Before you begin, make sure you have the following:

- An account with Salad Cloud. If you don't have one yet, you can sign up for a free trial at <https://portal.salad.com> .
- A project in Salad Cloud. If you don't have a project yet, you can create one by following the instructions in the Salad Cloud documentation.
- A container image that you want to deploy. If you don't have a container image yet, you can build one using a tool like **[Docker.](https://www.docker.com/)**

## **Step 1: Obtain Your API Key**

To authenticate your API requests, you'll need an API key. To obtain your API key, follow these steps:

- Log in to your Salad Cloud account at <https://portal.salad.com>
- Click on your profile in the top right corner of the page, then click API Keys.
- Copy the API key that is displayed. You'll need this in the next step. 

## **Step 2: Deploy the Container Image**

To deploy the container image, you'll need to send a POST request to the following URL:

```json Copy code
https://api.salad.com/api/public/organizations/organization_name/projects/project_name/containers \
```

Replace `{organization_name}` and `{project_name}` with the name of your organization and project, respectively.

Here's an example of how to send the POST request using `curl` :

```json Copy code
curl --request POST \
     --url https://api.salad.com/api/public/organizations/organization_name/projects/project_name/containers \
     --header 'accept: application/json' \
     --header 'content-type: application/json'
```

Replace `{API_KEY}` with your API key, and `{CONTAINER_IMAGE_URL}` with the URL of the container image you want to deploy.

## **Step 3: Check the Deployment Status**

After you send the POST request, Salad Cloud will begin the process of deploying your container image. To check the status of the deployment, you can send a GET request to the following URL:

```json Copy code
https://api.salad.com/api/public/organizations/organization_name/projects/project_name/containers/container_group_name \
```

Replace `{organization_name}` , `{project_name}` , and `{container_id}` with the name of your organization, project, and the container you want to check, respectively.

Here's an example of how to send the **GET** request using `curl` :

```json Copy code
curl --request GET \
     --url https://api.salad.com/api/public/organizations/organization_name/projects/project_name/containers/container_group_name \
     --header 'accept: application/json'
```

Replace `{API_KEY}` with your API key.

The response will include the current status of the deployment, as well as other details about the container.