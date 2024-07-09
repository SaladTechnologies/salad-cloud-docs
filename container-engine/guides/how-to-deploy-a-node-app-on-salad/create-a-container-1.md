---
title: "Create a container"
slug: "create-a-container-1"
excerpt: ""
hidden: true
metadata: 
  image: []
  robots: "index"
createdAt: "Mon Dec 26 2022 04:16:46 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Fri Oct 20 2023 07:49:20 GMT+0000 (Coordinated Universal Time)"
---
## **What is a Container? **

A container is a lightweight standalone executable package that contains everything needed to run an application, such as libraries, tools, runtime, settings, or code making it easy to deploy in VMs (Virtual Machines). It can be created as many as possible from a **single Docker image  
**

## To dockerize a Node.js application, we will need to follow these steps:

- A Node.js Application (**which we already have running on port 5000**)
- Create a Dockerfile
- Building a Docker Image
- Containerize the Docker image

## **What is a Dockerfile?**

A dockerfile is an ingredient or set of instructions needed to create a docker image(s). It gets to build the image by running the build command.

**Create a file in the root directory called Dockerfile.**  
First, we need to define which image we want to build from. 

Here we will use version 16 of the node available as it is the current version of _Nodejs_ as at this time this guide was written from Docker Hub : 

```dockerfile
FROM node:16.18.0

#Create app directory
WORKDIR /app

#Install the app dependencies using the npm binary.
COPY package*.json  ./
 
RUN npm install

#Copy the rest of the application to the app directory.
COPY . /app
 
#Expose the port and start the application. 
EXPOSE 5000
 
CMD [ "npm", "start" ]
```

**NOTE:** Above you will notice we used two distinct **COPY** commands to reduce the application rebuild time

## ** Create a `.dockerignore` file **

**What is a .dockerignore file: **  
It helps prevent the local module and debug logs from being copied into your Docker image when building a docker image.

Now, let's create  a **`.dockerignorefile`** file so as not to copy unnecessary files to the container during its built process from the logs. 

```dockerfile .dockerignorefile
npm-debug.log
/node_modules
```

This prevents the local module and debug logs from being interrupted and copied onto your Docker image.

## **Building your Docker Image**

## **What is a Docker Image: **

This is a set of read-only instructions that helps to build a container and makes it possible to run it on a Docker.  
Building your Docker image is quite easy and can be done using a single command.

But before building it, look at the image below to confirm you have the displayed files and directories on your code editor. If you can’t or don’t have the codes. 

You can** [fork a folder repo here](https://github.com/SaladTechnologies/salad-docs)** from this to build yours.

![](https://files.readme.io/a1949a2-vscode.PNG "vscode.PNG")

Be sure to have these extensions installed so you can remotely access your docker logs and files via your Vscode just like this image below:

- **Docker extension**
- **Dev Container extension**
- **Remote SSH extension **

On the left section of this picture, you can see the **Docker extension, Remote live server,** and **Dev container extension icons.  
** 

![](https://files.readme.io/70f9396-dockk.PNG "dockk.PNG")


Be sure to install and download these two extensions if you are using Vscode (Visual Studio Code) so you can access your images and containers on your visual code editor registry easily.

On the left-hand side of your Vscode via the docker tab.  
The docker image on the left pane of the code editor shows that it is installed as an extension and you can also access the Docker hub and Registry within your Vscode environment.

It should look something like this below: 

![](https://files.readme.io/b8ad601-docker_imm.PNG "docker imm.PNG")

If confirmed, you can run this command on your terminal or CLI tool. 

```text Copy command
Docker build -t <docker-image-name> <filepath> .
```

The **`-t flag`** lets you tag your image so it’s easier to find later

Here is an example we use in this guide:

```text Copy command
Docker build -t nodejs-app .
```

The result should look like this in the terminal with a message above **"FINISHED"** 

![](https://files.readme.io/07dd15c-docker_build.PNG "docker build.PNG")

You should get something similar to the output above after executing the command.  
This means that the docker image was created successfully and the app is working.

Now that the build is complete, you can check your image or your docker using this docker command below :

```text Copy command
docker image ls
```

Here is the result:

![](https://files.readme.io/4970664-Capture.PNG "Capture.PNG")

## **Check Using your Docker Desktop:**

- **Open your Docker Desktop **
- **Go to Images on the left side of your docker desktop dashboard**

You can see your built Nodejs docker image there.

![](https://files.readme.io/d98a826-hio.PNG "You can see the \"nodejs-app\" container image name")


## **Create a Container using Docker Desktop:**

You will need to create a container from your built image.  
You can easily do that using your Docket desktop with the following steps.

1. Go to your **Docker desktop** and navigate to your Image tab

![](https://files.readme.io/422af67-hio.PNG "You can see the container image on the image tab on Docker Desktop")


1. Go to your created and built docker image from your application. The one we used here is named  "_node-app_"

![](https://files.readme.io/f291669-vogue.PNG "This pop-up shows you the process to run your created container")


1. Before clicking on "RUN " from the image tab, Click on the “Optional settings “ specify a favorable container name or it will generate a random one for you.  
   Then route the host to your local server application 

Example: Localhost:5000. By typing your **`local host port (5000),`** which is what we are using. Yours can be 8080 or anything. 

![](https://files.readme.io/2f6c635-bbb.PNG "bbb.PNG")

Launch **Run.** You have successfully created a container. You can view this via your container tab above the image tab on your Docker desktop. 

![](https://files.readme.io/53a21ad-running.PNG "\"node-app\" is running on port 5000")


Navigate to actions and choose "Logs" to view your running container logs. 

![](https://files.readme.io/49a6b5f-logs.PNG "The server is running on port: 5000")

Navigate to your browser and type in or paste " https\://localhost:5000" to view your running container image with display message " Hello world "

![](https://files.readme.io/0eaeedd-hello_world.PNG "Nodejs container image running on localhost:5000 showing \"Hello world\" message")


## **Run a Container Using the terminal or command line  **

Do note that a container can be created as many times as you want.  
Now we can run the docker image using the command:

```text Docker run command
Docker run -d -p <Host port>:<Docker port><docker-image-name>
```

The **`-d flag`** indicates the docker container is running in the background.

The **`-p flag`** shows which host port will be connected to the docker port.

Example:

```text Copy command
Docker run -d -p 5000:5000 nodejs-app
```

Result:

![](https://files.readme.io/2f15317-hello_world.PNG "hello world.PNG")
