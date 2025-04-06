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
## 1.3 Setting Up an ECS Cluster

This section guides you through the process of creating an Amazon ECS (Elastic Container Service) cluster, which is a logical grouping of container instances that you can use to run tasks. For this chatbot application, we'll use the Fargate launch type, which allows you to run containers without managing the underlying EC2 instances.

#### 1.3.1 Create ECS Cluster

1.  **Go to the Amazon ECS Console:** Open your web browser and navigate to the AWS Management Console. Search for "ECS" and click on "Elastic Container Service".

2.  **Click "Create Cluster":** On the ECS dashboard, you'll see a button labeled "Create Cluster". Click on it to start the cluster creation wizard.

3.  **Choose the "Networking Only (Fargate)" cluster template:** In the cluster template selection step, select the option labeled **"Networking Only"** and ensure that the **"Powered by AWS Fargate"** option is chosen. This template is designed for running containers directly on AWS Fargate without managing EC2 instances.

4.  **Configure Cluster Settings:**
    * **Cluster name:** Enter a descriptive name for your ECS cluster, for example, `ai-chatbot-cluster`. **Make a note of this cluster name**, as you'll need it later when configuring your GitHub Actions workflow and ECS services.
    * **VPC and Subnets (Optional but Recommended):** While Fargate handles the underlying infrastructure, you can choose the VPC (Virtual Private Cloud) and subnets where your tasks will run. It's generally recommended to select a VPC with public and private subnets configured for better network isolation and security. If you don't have a specific VPC in mind, AWS will use your default VPC.
    * **Security Group (Optional but Recommended):** You can configure a security group for the Fargate tasks within this cluster. This acts as a virtual firewall, controlling inbound and outbound traffic for your containers. You might want to allow inbound traffic on specific ports (e.g., port 80 or 443 for the frontend).
    * **Tags (Optional):** You can add tags to your ECS cluster for better organization and cost tracking.

5.  **Click "Create":** After configuring the cluster settings, review your choices and click the "Create" button to provision your ECS cluster. The cluster will be created within a few minutes.

## 1.4 Creating ECS Services for Frontend and Backend

An ECS service manages the running of tasks of a specific task definition within your cluster. It ensures that the desired number of tasks are running and automatically replaces any tasks that fail. You'll need to create separate services for your backend and frontend applications.

#### 1.4.1 Backend Service

1.  **Go to the ECS Console and choose "Services" under your ECS cluster:** Navigate to the ECS console, select the cluster you just created (`ai-chatbot-cluster`), and then click on the "Services" tab in the cluster details.

2.  **Click "Create":** Click the "Create" button to start creating a new ECS service.

3.  **Configure Service:**
    * **Launch type:** Ensure "FARGATE" is selected.
    * **Task definition:** Choose the **`ai-chatbot-backend`** task definition from the dropdown menu. This task definition specifies the Docker image, resource requirements, and other configurations for your backend container.
    * **Cluster:** Your newly created cluster (`ai-chatbot-cluster`) should be pre-selected.
    * **Service name:** Enter a name for your backend service, for example, `ai-chatbot-backend-service`. **Make a note of this service name.**
    * **Number of tasks:** Set the desired number of instances of your backend application you want to run. For example, setting it to `2` will ensure that two backend containers are always running. ECS will automatically manage their lifecycle.
    * **Deployment configuration:** Leave the default settings (Rolling update) for now.
    * **Networking:**
        * **VPC and Subnets:** Select the VPC and subnets where you want your backend tasks to run. These should typically be private subnets if your backend doesn't need direct public internet access.
        * **Security groups:** Choose the security group(s) that will be associated with your backend tasks. Ensure that it allows necessary inbound traffic (if any) and outbound traffic.
    * **Load balancing (Optional but Recommended for scaling and availability):** If you plan to have multiple backend instances and want to distribute traffic, you can configure a load balancer. If so:
        * Choose "Application Load Balancer" or "Network Load Balancer".
        * Select an existing load balancer or create a new one.
        * Configure the listener and target group to route traffic to your backend containers on the appropriate port (as defined in your backend task definition's container port mapping).
    * **Health checks:** Configure health checks to monitor the health of your backend containers. ECS will use these checks to determine if a task is healthy and should receive traffic (if using a load balancer).

4.  **Click "Create service":** Review your configuration and click the "Create service" button.

#### 1.4.2 Frontend Service

1.  **Similarly, create a service for the frontend:** Follow the same steps as above (go to the ECS console, select your cluster, click "Services", and then "Create").

2.  **Configure Frontend Service:**
    * **Launch type:** Ensure "FARGATE" is selected.
    * **Task definition:** Choose the **`ai-chatbot-frontend`** task definition.
    * **Cluster:** Your cluster (`ai-chatbot-cluster`) should be selected.
    * **Service name:** Enter a name for your frontend service, for example, `ai-chatbot-frontend-service`. **Make a note of this service name.**
    * **Number of tasks:** Set the desired number of frontend instances (e.g., `1` or more).
    * **Deployment configuration:** Leave the default settings.
    * **Networking:**
        * **VPC and Subnets:** Select the VPC and **public** subnets where you want your frontend tasks to run, as they will likely need to be accessible from the internet.
        * **Security groups:** Choose the security group(s) for your frontend tasks. Ensure it allows inbound traffic on the port your frontend application listens on (e.g., port 80 for HTTP, port 443 for HTTPS).
    * **Load balancing (Crucial for the Frontend):** The frontend service typically needs to be accessible via a web browser, so an Application Load Balancer (ALB) is essential for routing traffic to your frontend containers.
        * Choose "Application Load Balancer".
        * Select an existing ALB or create a new one.
        * Configure the listener (e.g., on port 80 or 443) and target group. The target group should forward traffic to the port your frontend container is listening on (as defined in its task definition).
        * Ensure your ALB is configured with appropriate security group rules to allow inbound traffic from the internet (e.g., HTTP on port 80, HTTPS on port 443).

3.  **Click "Create service":** Review your frontend service configuration and click "Create service".

## 1.5 IAM Roles and Policies

IAM (Identity and Access Management) roles and policies are crucial for granting necessary permissions to your ECS tasks and the ECS service itself. You need to ensure the following roles are in place:

* **ECS Task Execution Role:** This IAM role is assumed by the ECS agent running on the Fargate infrastructure. It grants ECS the permissions it needs to manage your tasks on your behalf. This typically includes permissions to:
    * **Pull Docker images from Amazon ECR:** Allows ECS to download the container images specified in your task definitions.
    * **Write logs to Amazon CloudWatch Logs:** Enables your container logs to be sent to CloudWatch for monitoring and troubleshooting.
    * **Potentially interact with other AWS services** depending on your task definition (e.g., Secrets Manager if you're retrieving secrets that way).

    **When creating your ECS task definition, you will specify this Task Execution Role.** You likely created this role when setting up ECS for the first time or you can create a new one in the IAM console with the `AmazonECSTaskExecutionRolePolicy` attached. **Make a note of the ARN (Amazon Resource Name) of this ECS Task Execution Role.**

* **Task Role:** This IAM role is assumed by the containers running within your ECS tasks (i.e., your backend and frontend applications). It grants your application code the permissions it needs to access other AWS resources. For your chatbot application, this role might need permissions to:
    * **Access secrets stored in AWS Secrets Manager:** If you are following the recommended practice of storing your Google API key (and potentially other sensitive information) in Secrets Manager, your task role needs permission to read these secrets.
    * **Interact with other AWS services:** Depending on your application's functionality, it might need permissions to access databases (e.g., RDS, DynamoDB), message queues (e.g., SQS, SNS), or other AWS resources.

    **You will create separate Task Roles for your backend and frontend if they require different sets of permissions. When creating your ECS task definitions (`ai-chatbot-backend` and `ai-chatbot-frontend`), you will specify the appropriate Task Role for each.** You can create these roles in the IAM console and attach policies that grant the necessary permissions. **Make a note of the ARNs of your backend and frontend Task Roles.**

**In summary, ensure you have created the following IAM roles and noted their ARNs:**

* **ECS Task Execution Role ARN:** Used by the ECS agent.
* **Backend Task Role ARN:** Used by your backend containers.
* **Frontend Task Role ARN:** Used by your frontend containers.

You will need these ARNs when configuring your ECS task definitions and potentially in other parts of your AWS setup.

## 2. CI/CD Pipeline with GitHub Actions

This section describes how to create a Continuous Integration/Continuous Deployment (CI/CD) pipeline using GitHub Actions to automate the build and deployment of your backend and frontend applications to Amazon ECS.

### 2.1 GitHub Actions Workflow for Backend and Frontend

You need to create a file named `.github/workflows/deploy.yml` in the root of **each** of your repositories (both the backend and the frontend repositories). This workflow file defines the automated process that will run whenever code is pushed to the `main` branch.

```yaml
name: Deploy to ECS

# This defines when the workflow will trigger.
on:
  push:
    branches:
      - main # The workflow will run when code is pushed to the 'main' branch.

# Defines the jobs that will be executed in the workflow.
jobs:
  build-and-deploy:
    # Specifies the type of machine to run the job on.
    runs-on: ubuntu-latest

    # Defines the sequence of tasks to be executed in the job.
    steps:
      # Step 1: Checkout code
      # This action checks out your repository code from GitHub onto the runner.
      - name: Checkout code
        uses: actions/checkout@v2

      # Step 2: Set up Docker Buildx
      # Docker Buildx is a CLI plugin that extends the functionality of the docker build command with support for builder instances and new features.
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      # Step 3: Log in to Amazon ECR
      # This action authenticates the GitHub Actions runner with your Amazon Elastic Container Registry (ECR).
      # It uses the AWS credentials configured as GitHub Secrets (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY).
      - name: Log in to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v1

      # Step 4: Build Docker images
      # This step builds the Docker images for your backend and frontend applications.
      # It assumes that you have Dockerfiles in the root of your respective repositories.
      - name: Build Docker images
        run: |
          docker build -t ai-chatbot-backend .  # Builds the backend image, tagging it as 'ai-chatbot-backend'
          docker build -t ai-chatbot-frontend .  # Builds the frontend image, tagging it as 'ai-chatbot-frontend'

      # Step 5: Tag Docker images
      # This step tags the locally built Docker images with the full ECR repository URI.
      # This is necessary for pushing the images to the correct ECR repository.
      # You need to replace `<aws_account_id>` and `<region>` with your actual AWS account ID and region.
      - name: Tag Docker images
        run: |
          docker tag ai-chatbot-backend:latest <aws_account_id>.dkr.ecr.<region>[.amazonaws.com/ai-chatbot-backend:latest](https://www.google.com/search?q=https://.amazonaws.com/ai-chatbot-backend:latest)
          docker tag ai-chatbot-frontend:latest <aws_account_id>.dkr.ecr.<region>[.amazonaws.com/ai-chatbot-frontend:latest](https://www.google.com/search?q=https://.amazonaws.com/ai-chatbot-frontend:latest)

      # Step 6: Push Docker images to ECR
      # This step pushes the tagged Docker images to your Amazon ECR repositories.
      # Ensure that the ECR repositories (ai-chatbot-backend and ai-chatbot-frontend) exist in your AWS account.
      - name: Push Docker images to ECR
        run: |
          docker push <aws_account_id>.dkr.ecr.<region>[.amazonaws.com/ai-chatbot-backend:latest](https://www.google.com/search?q=https://.amazonaws.com/ai-chatbot-backend:latest)
          docker push <aws_account_id>.dkr.ecr.<region>[.amazonaws.com/ai-chatbot-frontend:latest](https://www.google.com/search?q=https://.amazonaws.com/ai-chatbot-frontend:latest)

      # Step 7: Update ECS service for Backend
      # This step instructs ECS to update the backend service with the newly pushed Docker image.
      # `--cluster ai-chatbot-cluster`: Specifies the name of your ECS cluster.
      # `--service ai-chatbot-backend-service`: Specifies the name of your backend ECS service.
      # `--force-new-deployment`: Forces a new deployment of the service, ensuring the latest image is pulled and the tasks are updated.
      # You need to have the AWS CLI configured in your GitHub Actions environment (which is done by the ecr-login action).
      - name: Update ECS service for Backend
        run: |
          aws ecs update-service --cluster ai-chatbot-cluster --service ai-chatbot-backend-service --force-new-deployment

      # Step 8: Update ECS service for Frontend
      # This step does the same as the previous step but for the frontend ECS service.
      # `--cluster ai-chatbot-cluster`: Specifies the name of your ECS cluster.
      # `--service ai-chatbot-frontend-service`: Specifies the name of your frontend ECS service.
      # `--force-new-deployment`: Forces a new deployment of the service.
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









