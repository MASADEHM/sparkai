# SparkAI Deployment Guide

This guide covers deploying SparkAI to Azure using Docker Desktop on Windows.

## Prerequisites

1. **Docker Desktop** - Install from [docker.com](https://www.docker.com/products/docker-desktop)
2. **Azure CLI** - Install from [Microsoft](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows)
3. **Azure Account** with an active subscription
4. **Azure Container Registry** (ACR) - Either existing or create new
5. **.env file** with your Azure OpenAI credentials

## Architecture

The application consists of two containers:
- **Backend**: FastAPI application with LangGraph agents and RAG capabilities
- **Frontend**: Streamlit web interface

## Deployment Steps

### Step 1: Prepare Your Environment

1. Ensure your `.env` file exists with these variables:
```env
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
OPENAI_API_KEY=your_api_key
AZURE_OPENAI_CHAT_MODEL=your_chat_model
AZURE_OPENAI_EMEBDDING_DEPLOYMENT=your_embedding_deployment
AZURE_OPENAI_EMEBDDING_MODEL=your_embedding_model
AZURE_OPENAI_API_EMEBDDING_VERSION=your_api_version
```

2. Start Docker Desktop

3. Login to Azure CLI:
```powershell
az login
```

### Step 2: Test Locally (Optional but Recommended)

Test the application locally using Docker Compose:

```powershell
.\test-local.ps1
```

This will:
- Build both backend and frontend images
- Start both services
- Backend available at: http://localhost:8000
- Frontend available at: http://localhost:8501

Press `Ctrl+C` to stop the services.

### Step 3: Build and Push to Azure Container Registry

1. Update the `build-and-push.ps1` script with your ACR name:
```powershell
$ACR_NAME = "crfb01"  # Your ACR name (without .azurecr.io)
$IMAGE_VERSION = "1.2"  # Version number
```

2. Run the build and push script:
```powershell
.\build-and-push.ps1
```

This will:
- Login to your ACR
- Build backend Docker image
- Build frontend Docker image
- Tag both images (with version and 'latest')
- Push both images to ACR

### Step 4: Deploy to Azure Container Apps

#### Option A: Using Azure Portal (Easiest)

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new **Container Apps Environment** (if you don't have one)
3. Create **Backend Container App**:
   - Image: `crfb01.azurecr.io/sparkai-backend:latest`
   - Ingress: Enabled, External
   - Target port: 8000
   - Add all environment variables from your `.env` file
4. Create **Frontend Container App**:
   - Image: `crfb01.azurecr.io/sparkai-frontend:latest`
   - Ingress: Enabled, External
   - Target port: 8501
   - Environment variable: `API_URL=https://[backend-url]`

#### Option B: Using PowerShell Script

Run the deployment script:
```powershell
.\deploy-azure.ps1 -ResourceGroup "sparkai-rg" -AcrName "crfb01" -Location "eastus"
```

This will:
- Create resource group
- Create Container Apps environment
- Deploy both backend and frontend
- Configure networking between them

### Step 5: Configure Environment Variables

After deployment, add your Azure OpenAI secrets to the backend container app:

```powershell
az containerapp update `
    --name sparkai-backend `
    --resource-group sparkai-rg `
    --set-env-vars `
        AZURE_OPENAI_ENDPOINT="your_endpoint" `
        OPENAI_API_KEY="your_key" `
        AZURE_OPENAI_CHAT_MODEL="your_model" `
        AZURE_OPENAI_EMEBDDING_DEPLOYMENT="your_embedding" `
        AZURE_OPENAI_EMEBDDING_MODEL="your_embedding_model" `
        AZURE_OPENAI_API_EMEBDDING_VERSION="your_version"
```

## Manual Deployment (Original Method)

If you prefer the manual approach from the README:

```bash
# Build backend image
docker build -t sparkai:1.1 .

# Login to ACR
az acr login -n crfb01.azurecr.io

# Tag the image
docker tag sparkai:1.1 crfb01.azurecr.io/sparkai:1.1

# Push to ACR
docker push crfb01.azurecr.io/sparkai:1.1
```

## Useful Commands

### View images in Docker Desktop
```powershell
docker images
```

### View running containers
```powershell
docker ps
```

### View logs
```powershell
# Local
docker-compose logs -f

# Azure
az containerapp logs show --name sparkai-backend --resource-group sparkai-rg --follow
```

### Update a deployed app
```powershell
# After pushing new images to ACR
az containerapp update `
    --name sparkai-backend `
    --resource-group sparkai-rg `
    --image crfb01.azurecr.io/sparkai-backend:latest
```

### Stop local services
```powershell
docker-compose down
```

## Troubleshooting

### Docker Desktop Issues
- Ensure Docker Desktop is running
- Check Docker Desktop settings → Resources → ensure enough memory (4GB+ recommended)
- Try restarting Docker Desktop

### ACR Login Issues
- Run `az login` again
- Check your subscription: `az account show`
- Verify ACR exists: `az acr show --name crfb01`

### Build Failures
- Check `.env` file is present (for backend)
- Ensure all files are in correct locations
- Check Docker Desktop has enough disk space

### Container App Issues
- Check logs: `az containerapp logs show --name sparkai-backend --resource-group sparkai-rg`
- Verify environment variables are set correctly
- Check ingress is enabled
- Verify ACR credentials are configured

## Costs

Azure Container Apps pricing:
- Pay only for what you use
- Free tier includes 180,000 vCPU-seconds and 360,000 GiB-seconds per month
- Estimate: ~$20-50/month for development/testing

## Security Best Practices

1. **Never commit `.env` files** to git
2. **Use Azure Key Vault** for production secrets
3. **Enable managed identity** for ACR access (instead of admin credentials)
4. **Restrict ingress** to specific IPs if possible
5. **Use HTTPS** always (Container Apps provides free SSL)

## Next Steps

- Set up CI/CD pipeline with GitHub Actions
- Configure custom domain
- Set up monitoring and alerts
- Implement automatic scaling rules
- Add Application Insights for telemetry

