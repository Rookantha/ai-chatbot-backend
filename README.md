## Deployment Guide for AI Chatbot

This guide explains the step-by-step process of deploying the containerized frontend (Next.js) and backend (Python FastAPI) services to AWS Elastic Container Service (ECS) using the Fargate launch type. It also outlines the process of setting up a CI/CD pipeline with GitHub Actions to automate the deployment process.

## 1. AWS ECS Deployment:

### 1.1 Pushing Docker Images to Amazon Elastic Container Registry (ECR)

Before deploying to ECS, you need to push your Docker images to AWS ECR (Elastic Container Registry). Follow these steps:

#### 1.1.1 Create ECR Repositories

1.  Go to the [Amazon ECR Console](https://console.aws.amazon.com/ecr/repositories).
2.  Click **Create Repository** for both frontend and backend containers.
3.  Make a note of the ECR repository URIs (e.g., `123456789012.dkr.ecr.us-west-2.amazonaws.com/ai-chatbot-backend`).

#### 1.1.2 Build and Tag Docker Images

In your local terminal, navigate to the frontend and backend directories, and run the following commands to build and tag your Docker images:

```bash
# Backend
docker build -t ai-chatbot-backend .
docker tag ai-chatbot-backend:latest <aws_account_id>.dkr.ecr.<region>[.amazonaws.com/ai-chatbot-backend:latest](https://www.google.com/search?q=https://.amazonaws.com/ai-chatbot-backend:latest)

# Frontend
docker build -t ai-chatbot-frontend .
docker tag ai-chatbot-frontend:latest <aws_account_id>.dkr.ecr.<region>[.amazonaws.com/ai-chatbot-frontend:latest](https://www.google.com/search?q=https://.amazonaws.com/ai-chatbot-frontend:latest)#### 1.1.3 Authenticate Docker to ECR
Use the AWS CLI to authenticate your local Docker client to ECR:
```
```bash

aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
```
#### 1.1.4 Push Docker Images
Push the tagged Docker images to your respective ECR repositories:

``` bash 
# Backend
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-backend:latest


# Frontend
docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-frontend:latest
```
### 1.2 Creating ECS Task Definitions for Frontend and Backend
An ECS Task Definition is a blueprint for your containers. You need to define resources like CPU, memory, environment variables, and container image URIs.

1.2.1 Backend Task Definition
Create a JSON file (backend-task-definition.json) for the backend service with the following contents:

```json
{
  "family": "ai-chatbot-backend",
  "executionRoleArn": "<ecs_task_execution_role>",
  "taskRoleArn": "<ecs_task_role>",
  "containerDefinitions": [
    {
      "name": "ai-chatbot-backend",
      "image": "<aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-backend:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {
          "name": "GOOGLE_API_KEY",
          "value": "<google_api_key>"
        }
      ]
    }
  ]
}
```
To replace the placeholders in your configuration, follow these steps:

1.  **Replace `<ecs_task_execution_role>`:**
    * Locate the ARN (Amazon Resource Name) of your ECS task execution IAM role. This role grants the ECS agent permissions to make calls to AWS APIs on your behalf.
    * Replace the text `<ecs_task_execution_role>` with the actual ARN.
    * **Example:** `arn:aws:iam::123456789012:role/ecsTaskExecutionRole`

2.  **Replace `<ecs_task_role>`:**
    * Locate the ARN of your ECS task IAM role specifically for your backend application. This role grants permissions to the containers in your backend task.
    * Replace the text `<ecs_task_role>` with the actual ARN.
    * **Example:** `arn:aws:iam::123456789012:role/backendTaskRole`

3.  **Replace `<aws_account_id>`:**
    * Find your 12-digit AWS account ID. You can typically find this in the AWS Management Console.
    * Replace the text `<aws_account_id>` with your actual AWS account ID.
    * **Example:** `123456789012`

4.  **Replace `<region>`:**
    * Specify the AWS region where your ECS cluster and resources are located (e.g., `us-east-1`, `eu-west-2`, `ap-southeast-2`).
    * Replace the text `<region>` with your desired AWS region.
    * **Example:** `us-west-2`

5.  **Replace `<google_api_key>`:**
    * Obtain your Google API key.
    * **Instead of hardcoding directly, consider using AWS Secrets Manager for better security:**
        * **Option 1: Using AWS Secrets Manager (Recommended)**
            1.  Store your Google API key as a secret in AWS Secrets Manager.
            2.  In your ECS task definition, configure an environment variable that retrieves the secret value from Secrets Manager. You'll need to define the `valueFrom` field in your container definition.
            3.  Replace `<google_api_key>` with the ARN of the secret you created in AWS Secrets Manager (or the appropriate Secrets Manager reference in your task definition).
            * **Example (in task definition environment variable):**
                ```json
                "environment": [
                  {
                    "name": "GOOGLE_API_KEY",
                    "valueFrom": "arn:aws:secretsmanager:us-west-2:123456789012:secret:my-google-api-key:SecretString:apiKey"
                  }
                ]
                ```
        * **Option 2: Hardcoding (Less Secure - Use with Caution)**
            * Replace the text `<google_api_key>` with your actual Google API key.
            * **Example:** `AIzaSy***************************************`

**Summary of Replacements (Example):**

Let's say your actual values are:

* ECS Task Execution Role ARN: `arn:aws:iam::987654321098:role/my-ecs-task-execution-role`
* ECS Task Role ARN: `arn:aws:iam::987654321098:role/my-backend-task-role`
* AWS Account ID: `987654321098`
* AWS Region: `ap-southeast-1`
* Google API Key (stored in Secrets Manager with ARN): `arn:aws:secretsmanager:ap-southeast-1:987654321098:secret:google-maps-key`

Then, the replacements would look like this:

#### 1.2.2 Frontend Task Definition
Similarly, create a frontend-task-definition.json for the frontend service:

``` json

{
  "family": "ai-chatbot-frontend",
  "executionRoleArn": "<ecs_task_execution_role>",
  "taskRoleArn": "<ecs_task_role>",
  "containerDefinitions": [
    {
      "name": "ai-chatbot-frontend",
      "image": "<aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-frontend:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "hostPort": 3000
        }
      ],
      "environment": [
        {
          "name": "NEXT_PUBLIC_API_URL",
          "value": "http://backend:8000"
        }
      ]
    }
  ]
}
```
#### 1.2.3 Register the Task Definitions
Register the ECS task definitions with the following commands:

``` bash

aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json
```

### 1.3 Setting Up an ECS Cluster
#### 1.3.1 Create ECS Cluster
Go to the Amazon ECS Console.

Click Create Cluster and choose the Networking Only (Fargate) cluster template.

Follow the steps to create the cluster and make a note of the cluster name.

### 1.4 Creating ECS Services for Frontend and Backend
#### 1.4.1 Backend Service
Go to the ECS Console and choose Services under your ECS cluster.

Click Create and select the ai-chatbot-backend task definition.

Set the desired number of tasks (e.g., 2) and configure the load balancer (if applicable).

Ensure the service runs in the correct VPC and subnets.

#### 1.4.2 Frontend Service
Similarly, create a service for the frontend using the ai-chatbot-frontend task definition.

Configure the frontend service to use the Application Load Balancer (ALB) for routing traffic.

### 1.5 IAM Roles and Policies
Ensure that the following IAM roles and policies are in place for ECS:

ECS Task Execution Role: Grants ECS permissions to pull images from ECR, log to CloudWatch, etc.

Task Role: Grants the backend and frontend services permission to access resources (e.g., secrets for API keys).

## 2. CI/CD Pipeline with GitHub Actions
### 2.1 GitHub Actions Workflow for Backend and Frontend
Create a .github/workflows/deploy.yml file in your repositories to automate the CI/CD pipeline.

``` yaml

name: Deploy to ECS

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Log in to Amazon ECR
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build Docker images
      run: |
        docker build -t ai-chatbot-backend .
        docker build -t ai-chatbot-frontend .

    - name: Tag Docker images
      run: |
        docker tag ai-chatbot-backend:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-backend:latest
        docker tag ai-chatbot-frontend:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-frontend:latest

    - name: Push Docker images to ECR
      run: |
        docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-backend:latest
        docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/ai-chatbot-frontend:latest

    - name: Update ECS service for Backend
      run: |
        aws ecs update-service --cluster ai-chatbot-cluster --service ai-chatbot-backend-service --force-new-deployment

    - name: Update ECS service for Frontend
      run: |
        aws ecs update-service --cluster ai-chatbot-cluster --service ai-chatbot-frontend-service --force-new-deployment
```

### 2.2 Managing Secrets in GitHub Actions

To securely store sensitive information like AWS credentials and your Google API Key for use in GitHub Actions, follow these steps:

1.  **Navigate to your GitHub repository Settings.**
2.  **Go to Secrets > Actions** in the left-hand sidebar.
3.  **Click "New repository secret"** (usually a green button).
4.  **Add the following secrets individually:**

    * **Name:** `AWS_ACCESS_KEY_ID`
        * **Secret:** Your actual AWS access key ID.

    * **Click "Add secret"**.

    * **Name:** `AWS_SECRET_ACCESS_KEY`
        * **Secret:** Your actual AWS secret access key.

    * **Click "Add secret"**.

    * **(Optional) For your Google API Key (recommended):**
        * **Name:** `GOOGLE_API_KEY`
        * **Secret:** Your actual Google API key.

    * **Click "Add secret"**.

Once these secrets are added, you can securely access them within your GitHub Actions workflows.

**Important Security Note:** Avoid hardcoding sensitive information directly in your workflow files. Using GitHub Secrets is a much more secure way to manage credentials.
``` yaml

env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```


## 3. Deliverables  
Frontend GitHub Repository URL: [https://github.com/Rookantha/ai-chatbot-frontend.git](https://github.com/Rookantha/ai-chatbot-frontend.git)  

Backend GitHub Repository URL: [https://github.com/Rookantha/ai-chatbot-backend.git](https://github.com/Rookantha/ai-chatbot-backend.git)  









