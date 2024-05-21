---
title: "Create Your first \"hello world\""
slug: "create-your-first-hello-world-1"
excerpt: ""
hidden: true
metadata: 
  image: []
  robots: "index"
createdAt: "Mon Dec 26 2022 04:16:04 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Fri Oct 20 2023 07:49:20 GMT+0000 (Coordinated Universal Time)"
---
## **Creating a _"hello world"_ Node.js Application**

First, we will start by creating a directory for our project and then install some dependencies for our simple “Hello world” app using the command line.

```shell Copy command
mkdir nodejs-server
 
cd nodejs-server
```

**Install npm And Express Framework: **  
Install npm and Express, which is a Node.js framework. 

**Then, initialize npm** in our directory.  
Copy or use the command below in your command line or terminal. 

```shell Install npm and dependencies
npm init
```

Above, **`npm`** creates a **`package.json`** that holds the dependencies of the app. 

**Next, **install the Express framework dependency.

```text Install Express
npm install express --save
```

Codebase should look like this below: 

```javascript Copy code
{
  "name": "node-app",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "license": "MIT",
  "dependencies":
  {
    "express": "^4.18.2"
  }
}
```

**Create an app.js file with an HTTP server that will return Hello world.** 

Here is the code below :

```javascript Copy code
const express = require('express');
const app = express();
 
// This tells the app which port to listen to
app.listen(process.env.PORT || 5000, () => {
    console.log(`Server is running on port`)
})
 
//This shows the response that will sent to the user
app.get("/", (req,res) => {
    res.send('Hello World')
})
```

**Now, Save this file above, open your terminal, CLI (Command Line) to run the application**

```shell Run this command
node app.js
```

The app is now ready to launch: 

It will show you on your terminal **_`Server is running on port 5000`_** 

![](https://files.readme.io/e15a288-node.PNG "node.PNG")

Go to your browser, copy and paste ** `http://localhost:8080/` ** in your browser to view it.

Here is a **_“Hello world”_** output on my browser :

![](https://files.readme.io/77b4901-hello_world.PNG "hello world.PNG")
