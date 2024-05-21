---
title: "JupyterLab"
slug: "jupyterlab"
excerpt: "Create and run your own GPU-accelerated JupyterLab on SaladCloud!"
hidden: false
createdAt: "Sat Jan 27 2024 00:24:51 GMT+0000 (Coordinated Universal Time)"
updatedAt: "Tue Apr 09 2024 16:16:59 GMT+0000 (Coordinated Universal Time)"
---
By running JupyterLab over SaladCloud, college students and professionals in the AI and Data Science industry can access the world’s most affordable GPU-accelerated platform to learn CUDA and PyTorch/TensorFlow programming, as well as to test and research various AI models for training, fine-tuning and inference. This not only contributes to cost reduction by eliminating the need to purchase expensive hardware but also saves time and effort associated with building dedicated development environments. Additionally, it fosters collaboration by providing a platform for sharing insights and collaborating with peers.

SaladCloud offers several pre-built JupyterLab container images in Docker Hub, designed to fulfill general requirements. You have the option to run these images directly on SaladCloud for your AI/ML tasks. Alternatively, you can customize them to meet specific needs by utilizing the Dockerfile templates available on our GitHub repository.

[Docker Hub repository](https://hub.docker.com/r/saladtechnologies/jupyterlab)

[GitHub repository](https://github.com/SaladTechnologies/jupyterlab)

[block:parameters]
{
  "data": {
    "h-0": "Container Image",
    "h-1": "Features ",
    "0-0": "saladtechnologies/jupyterlab:1.0.0-pytorch-tensorflow-cpu-aws-azure-gcp",
    "0-1": "JupyterLab  \nHugging Face transformers and datasets  \nAutoAWQ 0.1.6  \nPyTorch 2.1 GPU  \nPython 3.10  \nCUDA 11.8, cuDNN 8.7  \nIntegration with AWS S3, Azure Storage Account and GCP Cloud Storage",
    "1-0": "saladtechnologies/jupyterlab:1.0.0-pytorch-gpu-aws-azure-gcp",
    "1-1": "JupyterLab  \nHugging Face transformers and datasets  \nTensorFlow 2.13 GPU  \nPython 3.8  \nCUDA 11.2 (NVCC), cuDNN 8.1  \nIntegration with AWS S3, Azure Storage Account and GCP Cloud Storage",
    "2-0": "saladtechnologies/jupyterlab:1.0.0-tensorflow-gpu-aws-azure-gcp",
    "2-1": "JupyterLab  \nHugging Face transformers and datasets  \nPyTorch 2.1 CPU  \nTensorFlow 2.15 CPU  \nPython 3.10  \nIntegration with AWS S3, Azure Storage Account and GCP Cloud Storage"
  },
  "cols": 2,
  "rows": 3,
  "align": [
    "left",
    "left"
  ]
}
[/block]


# The construction of the JupyterLab container images

SaladCloud is designed to execute stateless container workloads. To ensure data persistence while using JupyterLab, we leverage storage services from public cloud platforms. The integration with major public cloud platforms, such as AWS, Azure, and GCP, is already implemented into the pre-built JupyterLab container images. Initial setup involves provisioning cloud storage in the chosen cloud platform, followed by using environment variables to pass the storage resource name and its access credentials to the container during launch.

We create a folder named 'data' within the /root directory of the container, acting as the current working directory that needs the data persistence. During the initial launch of the instance, a script file named ‘start.sh’ is executed, and all data is synchronized from the chosen cloud platform to the /root/data directory by use of Cloud-specific CLIs, the storage resource name and access credentials. Following this, the script continuously monitors the /root/data directory, and any changes (create, delete or modify) in this directory or its subfolders trigger the synchronization back to the cloud.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/bfebac8-tech_doc_1.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "500px",
      "border": true
    }
  ]
}
[/block]


Under the hood, we employ the inotifywait command-line tool that uses the inotify Linux kernel subsystem to watch for changes in the /root/data directory. Every time files are manually saved through the JupyerLab menu, or automatically saved by the JupyterLab’s autosave feature, the inotifywait command captures events such as create, delete or modify. Subsequently, the script triggers synchronization. All three public cloud platforms offer sync commands that can make the contents under the source the same as the content under the destination by calculating and copying only the differences instead of duplicating the entire directory. This integrated solution is highly effective, minimizing API calls to the cloud and reducing data transfer to the cloud to the minimum.

Models and datasets that are dynamically downloaded from Hugging Face or TensorFlow Hub are stored in the /root/.cache or /root/.keras hidden folders; and these data will be not synchronized to the cloud platform unless they are explicitly saved into the /root/data directory. Given that cloud storage typically incurs a charge of around $0.02 per GB Month (similar across all three cloud providers), the associated cost would be negligible if we mainly utilize the cloud storage for storing code.

For utilizing the pre-built JupyterLab container images, specific environment variables are required to pass information to containers. The Cloud-related environment variables can be omitted if data persistence is not required.

[block:parameters]
{
  "data": {
    "h-0": "Environment Variable",
    "h-1": "Description",
    "0-0": "JUPYTERLAB_PW",
    "0-1": "Define the password for JupyterLab.  \nCan be omitted, and the default password is ‘data’.",
    "1-0": "AWS_S3_BUCKET_FOLDER  \nAWS_ACCESS_KEY_ID  \nAWS_SECRET_ACCESS_KEY",
    "1-1": "Provide the AWS-related info to access a folder within an AWS S3 bucket.",
    "2-0": "AZURE_CONTAINER_URL  \nAZURE_BLOB_SAS_TOKEN",
    "2-1": "Provide the Azure-related info to access a container within an Azure storage account.",
    "3-0": "GOOGLE_BUCKET_FOLDER  \nGOOGLE_APPLICATION_CREDENTIALS  \nGOOGLE_PROJECT_ID",
    "3-1": "Provide the GCP-related info to access a folder within a GCP Cloud Storage bucket."
  },
  "cols": 2,
  "rows": 4,
  "align": [
    "left",
    "left"
  ]
}
[/block]


For the Dockerfile templates and the start.sh script file, please refer to our GitHub repository.

All major public cloud platforms, such as AWS, Azure, and GCP, offer the object storage service suitable for preserving data for the JupyterLab containers. The integration methods with the three cloud platforms are similar: provision the storage resource, obtain its access credentials, and then pass this information to launch a container.

If you are a business customer, such as a college, offering the JupyterLab service to numerous users, and each user requires exclusive access their own data, we recommend AWS. It provides a straightforward and simple implementation that allows multiple users to access their individual folders named with their usernames within the same bucket. In the event that a user's access credentials are compromised, the impact is confined to that specific user, safeguarding others from any potential consequences.

For individual customers, there is little significant difference among the three cloud platforms, and you can choose the cloud provider based on your preference.

# Provision the cloud storage in AWS

### Step 1: Create an AWS S3 bucket and a folder inside the S3 bucket

Log into the AWS Console, and create an AWS S3 bucket ('rxjupyterlab') with the default settings in one of the AWS Regions, and create a folder named with an AWS IAM username ('user1') within the S3 bucket. This folder will be synchronized with the /root/data directory inside a JupyterLab container running on SaladCloud. If an organization is providing the JupyterLab service for numerous users and aims to ensure exclusive access to their own data, creating one folder per user within the same bucket is a recommended approach in AWS.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/2009ed8-tech_doc_2.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


### Step 2: Create an AWS IAM policy for exclusive access

Create an AWS IAM policy ('access_its_own_folder') using the provided JSON file. This policy will be attached to AWS IAM users, ensuring that each user can exclusively access their own folder in the same S3 bucket.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/0e960c6-tech_doc_3.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


Replace 'rxjupyterlab' with your AWS S3 bucket name in the JSON file:

```json
{
  "Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"s3:PutObject",
				"s3:GetObject",
				"s3:DeleteObject"
			],
			"Resource": "arn:aws:s3:::rxjupyterlab/${aws:username}/*"
		},
		{
			"Sid": "AllowListBucketOfASpecificUserPrefix",
			"Action": "s3:ListBucket",
			"Effect": "Allow",
			"Resource": "arn:aws:s3:::rxjupyterlab",
			"Condition": {
				"StringLike": {
					"s3:prefix": [
						"${aws:username}/*"
					]
				}
			}
		}
	]
}
```

### Step 3: Create an AWS IAM user and generate its credentials

Create an AWS IAM user ('user1') without the AWS Console access and attach the customer-managed AWS IAM policy ('access_its_own_folder') to the user.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/e1b930e-tech_doc_4.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/07a9f96-tech_doc_5.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


Generate the access key ID/secret access key for the AWS IAM user ('user1'). Copy and securely keep the credentials in a safe location.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/3c0975e-tech_doc_6.jpg",
        "",
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


When running the JupyterLab containers on SaladCloud with AWS as the backend cloud storage, three AWS-related environment variables are utilized to pass the access key ID/access key secret, as well as the bucket and folder name to the container.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/1c7bad0-tech_doc_7.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "400px",
      "border": true
    }
  ]
}
[/block]


# Provision the cloud storage in Azure

### Step 1: Create an Azure storage account and a container inside the storage account

Log into the Azure Console, and create an Azure Storage Account ('rxjupyterdata') with the default settings in one of the Azure Regions, and create a container ('data') within the storage account. This container will be synchronized with the /root/data directory inside a JupyterLab container running on SaladCloud. If an organization is providing the JupyterLab service for numerous users and aims to ensure exclusive access to their own data, creating one container per user within the same storage account is a recommended approach in Azure.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/4e89d2d-tech_doc_8.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


Navigate to the “Properties” menu on the left panel, and copy the container URL.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/9042ffc-tech_doc_9.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


### Step 2: Create an access policy and a shared access token for the Azure storage account container

For the access policy, you can define the start time, expiry time and permissions; all the 6 permissions are necessary for the data persistence of JupyterLab containers.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/07728a3-tech_doc_10.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


After creating the access policy for the Azure storage account container, generate the shared access token.  Copy and securely keep the Blob SAS token in a safe location.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/3afd7e5-tech_doc_11.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


When running the JupyterLab containers on SaladCloud with Azure as the backend cloud storage, two Azure-related environment variables are utilized to pass the container URL and Blob SAS token to the container.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/207b332-tech_doc_12.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "400px",
      "border": true
    }
  ]
}
[/block]


# Provision the cloud storage in GCP

### Step 1: Create a GCP cloud storage bucket and a folder in the bucket

Log into the GCP Console, and create a GCP Cloud Storage bucket ('rxjupyterlab') with the default settings in one of the GCP Regions, and create a folder ('sa1') within the bucket. This folder will be synchronized with the /root/data directory inside a JupyterLab container running on SaladCloud. If an organization is providing the JupyterLab service for numerous users and aims to ensure exclusive access to their own data, creating one bucket per user is a recommended approach in GCP.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/f2c9a5d-tech_doc_13.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


### Step 2: Create a service account and generate its credentials

Create a service account (‘sa1’) without permissions, and add a key for the service account.  Download the key’s JSON file and securely keep it in a safe location.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/c089355-tech_doc_14.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


### Step 3: Grant access to the bucket for the service account

Navigate to the “rxjupyterlab” bucket again and grant the “Storage Admin” role to the sa1 service account. Unlike AWS, GCP does not provide an easy way to grant access only to a specific folder inside the bucket. With the above role assignment, the sa1 service account will have access to the entire bucket.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/95b3117-tech_doc_15.jpg",
        "",
        ""
      ],
      "align": "center"
    }
  ]
}
[/block]


When running the JupyterLab containers on SaladCloud with GCP as the backend cloud storage, three GCP-related environment variables are utilized to pass the credentials (content of the downloaded JSON file), the bucket and folder name, and project ID to the container.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/8d925de-tech_doc_16.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "0px"
    }
  ]
}
[/block]


[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/7cdc53a-tech_doc_16.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "400px",
      "border": true
    }
  ]
}
[/block]


# Run JupyerLab over SaladCloud

To run a JupyterLab instance on SaladCloud, you can log in the SaladCloud Console and deploy the JupyterLab instance by selecting 'Deploy a Container Group' with the following parameters:

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/13b07e0-tech_doc_17-1.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


[block:parameters]
{
  "data": {
    "h-0": "Parameter",
    "h-1": "Value",
    "0-0": "Container Group Name",
    "0-1": "jupyterlab001  \n# Any name you prefer.",
    "1-0": "Image Source",
    "1-1": "saladtechnologies/jupyterlab:1.0.0-pytorch-tensorflow-cpu-aws-azure-gcp  \n# Or your tailored JupyterLab image.",
    "2-0": "Replica Count",
    "2-1": "1  \n# Can only be 1.",
    "3-0": "vCPU",
    "3-1": "2  \n# Based on the task need.",
    "4-0": "Memory",
    "4-1": "4 GB  \n# Based on the task need.",
    "5-0": "GPU",
    "5-1": "RTX 1650 (4 GB), RTX 2080 (8 GB), RTX 3060 (12 GB) or others  \n# You can choose multiple GPU types simultaneously, and SaladCloud will then select a node that matches one of the selected types.",
    "6-0": "Container Gateway",
    "6-1": "Enable, Port: 8000  \nUse Authentication: No",
    "7-0": "Environment Variables",
    "7-1": "# Provide the corresponding environment variables based on your needs.  \n  \n# JupyterLab Password  \nJUPYTERLAB_PW  \n  \n# AWS  \nAWS_ACCESS_KEY_ID  \nAWS_SECRET_ACCESS_KEY  \nAWS_S3_BUCKET_FOLDER  \n  \n# Azure  \nAZURE_CONTAINER_URL  \nAZURE_BLOB_SAS_TOKEN  \n  \n\\# GCP  \nGOOGLE_APPLICATION_CREDENTIALS  \nGOOGLE_BUCKET_FOLDER  \nGOOGLE_PROJECT_ID"
  },
  "cols": 2,
  "rows": 8,
  "align": [
    "left",
    "left"
  ]
}
[/block]


SaladCloud would take a few minutes to download the image to the selected node and run the container. Using the  Console, you can determine whether the JupyterLab instance is ready to use.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/e657944-tech_doc_18.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


After the instance is running, you can type the generated Access Domain Name in the browser’s address bar, enter the password provided by the JUPYTERLAB_PW environment variable, and begin using the JupyterLab service.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/4b5c193-tech_doc_19.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


Now you can write Python code to learn, test, fine-tune or train the popular AI models from Hugging Face. In case any libraries or dependencies are missing, you can install them online in the notebook or terminal. You may also build your own container images to include specific libraries and dependencies based on the provided Dockerfile templates.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/a0383df-tech_doc_20.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


In the JupyterLab terminal, you have the flexibility to use SH and BASH, and switch between them. Additionally, you can engage in C/C++ and CUDA programming by utilizing gcc and nvcc.

[block:image]
{
  "images": [
    {
      "image": [
        "https://files.readme.io/6599a2b-tech_doc_21.jpg",
        "",
        ""
      ],
      "align": "center",
      "sizing": "600px"
    }
  ]
}
[/block]


By sharing access to the JupyterLab instance, a team can collaborate on editing the same notebook or using the same terminal from different locations. Regarding the the JupyterLab terminal, any modifications made by one team member in the terminal will promptly reflect in another member’s browser and vice versa, similar to the screen sharing on WebEx or Zoom.
