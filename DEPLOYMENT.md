# SparkAI Deployment Guide

This guide covers deploying SparkAI to Azure Container Apps using Docker Desktop.

## Prerequisites

1. **Docker Desktop**: install from [docker.com](https://www.docker.com/products/docker-desktop)
2. **Azure CLI**: install from [Microsoft](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Azure account** with an active subscription
4. **Azure Container Registry** (ACR): an existing one, or create a new one
5. **`.env` file**: copy [.env.example](.env.example) to `.env` and fill in your values

## Architecture

The application consists of two containers:
- **Backend**: FastAPI application with LangGraph agents and RAG capabilities
- **Frontend**: Streamlit web interface

## Deployment Steps

### Step 1: Prepare Your Environment

1. Create your `.env` file:
```bash
cp .env.example .env
```

2. Start Docker Desktop

3. Log in to Azure CLI:
```bash
az login
```

### Step 2: Test Locally (Optional but Recommended)

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:8501

Press `Ctrl+C` to stop the services.

### Step 3: Build and Push to Azure Container Registry

```powershell
.\build-and-push.ps1 -AcrName <your-acr> -ImageVersion 1.2
```

This will:
- Log in to your ACR
- Build the backend and frontend Docker images
- Tag both images with the version and `latest`
- Push both images to ACR

### Step 4: Deploy to Azure Container Apps

1. Go to the [Azure Portal](https://portal.azure.com)
2. Create a **Container Apps Environment** if you don't have one
3. Create the **backend container app**:
   - Image: `<your-acr>.azurecr.io/sparkai-backend:latest`
   - Ingress: enabled, external
   - Target port: 8000
   - Add every variable from your `.env` file
4. Create the **frontend container app**:
   - Image: `<your-acr>.azurecr.io/sparkai-frontend:latest`
   - Ingress: enabled, external
   - Target port: 8501
   - Environment variables: `API_URL=https://<backend-url>`, plus the same `API_USERNAME` / `API_PASSWORD` as the backend

### Step 5: Configure Environment Variables

You can also set the backend variables from the CLI. The full list is in [.env.example](.env.example):

```powershell
az containerapp update `
    --name sparkai-backend `
    --resource-group <your-resource-group> `
    --set-env-vars `
        AZURE_OPENAI_ENDPOINT="your_endpoint" `
        AZURE_OPENAI_API_KEY="your_key" `
        API_USERNAME="your_username" `
        API_PASSWORD="your_password"
```

Store keys and passwords as [Container Apps secrets](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets) rather than plain environment variables.

## Useful Commands

### View logs
```bash
# Local
docker compose logs -f

# Azure
az containerapp logs show --name sparkai-backend --resource-group <your-resource-group> --follow
```

### Update a deployed app
```bash
# After pushing new images to ACR
az containerapp update \
    --name sparkai-backend \
    --resource-group <your-resource-group> \
    --image <your-acr>.azurecr.io/sparkai-backend:<version>
```

### Stop local services
```bash
docker compose down
```

## Troubleshooting

### Docker Desktop Issues
- Ensure Docker Desktop is running
- Check Docker Desktop settings → Resources and make sure it has enough memory (4GB+ recommended)
- Try restarting Docker Desktop

### ACR Login Issues
- Run `az login` again
- Check your subscription: `az account show`
- Verify the ACR exists: `az acr show --name <your-acr>`

### Container App Issues
- Check logs: `az containerapp logs show --name sparkai-backend --resource-group <your-resource-group>`
- Verify environment variables are set correctly
- Check ingress is enabled
- Verify ACR credentials are configured

## Costs

Azure Container Apps pricing:
- Pay only for what you use
- The free tier includes 180,000 vCPU-seconds and 360,000 GiB-seconds per month
- Estimate: ~$20-50/month for development/testing

## Security Best Practices

1. **Never commit `.env` files** to git
2. **Use Azure Key Vault** or Container Apps secrets for production secrets
3. **Enable managed identity** for ACR access instead of admin credentials
4. **Restrict ingress** to specific IPs if possible
5. **Always use HTTPS**. Container Apps provides free TLS certificates.
