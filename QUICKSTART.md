# 🚀 SparkAI - Quick Deployment Guide

## 3-Step Deployment with Docker Desktop

### ✅ Prerequisites
- [ ] Docker Desktop installed and running
- [ ] Azure CLI installed (`az --version` to check)
- [ ] Logged into Azure (`az login`)
- [ ] `.env` file with Azure OpenAI credentials

---

### 📦 Step 1: Test Locally (Optional)

```powershell
.\test-local.ps1
```
- Opens at: http://localhost:8501
- Press `Ctrl+C` to stop

---

### 🏗️ Step 2: Build & Push to ACR

**Edit `build-and-push.ps1` first:**
```powershell
$ACR_NAME = "crfb01"  # Your ACR name
$IMAGE_VERSION = "1.2"  # Your version
```

**Then run:**
```powershell
.\build-and-push.ps1
```

This builds and pushes:
- `crfb01.azurecr.io/sparkai-backend:1.2`
- `crfb01.azurecr.io/sparkai-frontend:1.2`

---

### ☁️ Step 3: Deploy to Azure

**Option A - Automated (Recommended):**
```powershell
.\deploy-azure.ps1 -ResourceGroup "sparkai-rg" -AcrName "crfb01" -Location "eastus"
```

**Option B - Azure Portal:**
1. Go to [portal.azure.com](https://portal.azure.com)
2. Create Container Apps Environment
3. Create 2 Container Apps:
   - **Backend**: `crfb01.azurecr.io/sparkai-backend:latest` (port 8000)
   - **Frontend**: `crfb01.azurecr.io/sparkai-frontend:latest` (port 8501)
4. Set environment variables on backend
5. Set `API_URL` on frontend to backend URL

---

## 🔧 Update Existing Deployment

When you make code changes:

```powershell
# 1. Increment version in build-and-push.ps1
$IMAGE_VERSION = "1.3"  # New version

# 2. Build and push
.\build-and-push.ps1

# 3. Update Azure Container App
az containerapp update --name sparkai-backend --resource-group sparkai-rg --image crfb01.azurecr.io/sparkai-backend:1.3
az containerapp update --name sparkai-frontend --resource-group sparkai-rg --image crfb01.azurecr.io/sparkai-frontend:1.3
```

---

## 📝 Set Environment Variables in Azure

After deployment, configure backend secrets:

```powershell
az containerapp update `
    --name sparkai-backend `
    --resource-group sparkai-rg `
    --set-env-vars `
        AZURE_OPENAI_ENDPOINT="your_endpoint" `
        OPENAI_API_KEY="your_key" `
        AZURE_OPENAI_CHAT_MODEL="gpt-4" `
        AZURE_OPENAI_EMEBDDING_DEPLOYMENT="text-embedding-ada-002" `
        AZURE_OPENAI_EMEBDDING_MODEL="text-embedding-ada-002" `
        AZURE_OPENAI_API_EMEBDDING_VERSION="2024-02-01"
```

---

## 🔍 Useful Commands

```powershell
# View Docker images
docker images

# View local containers
docker ps

# View Azure logs
az containerapp logs show --name sparkai-backend --resource-group sparkai-rg --follow

# Stop local services
docker-compose down

# List ACR images
az acr repository list --name crfb01 --output table
az acr repository show-tags --name crfb01 --repository sparkai-backend --output table
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker not running | Start Docker Desktop |
| ACR login fails | Run `az login` again |
| Build fails | Check `.env` file exists |
| Port 8000/8501 in use | Stop other services or change ports |
| Container not starting | Check logs with `docker logs <container-id>` |

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `build-and-push.ps1` | Build & push images to ACR |
| `test-local.ps1` | Test app locally |
| `deploy-azure.ps1` | Deploy to Azure Container Apps |
| `docker-compose.yml` | Local multi-container setup |
| `Dockerfile.streamlit` | Frontend container |
| `DEPLOYMENT.md` | Full deployment guide |
| `.dockerignore` | Files to exclude from images |

---

## 💰 Estimated Azure Costs

- **Development/Testing**: $20-50/month
- **Production**: $50-200/month (depends on usage)
- Free tier includes 180,000 vCPU-seconds/month

---

## 🎯 Next Steps

- [ ] Set up custom domain
- [ ] Configure monitoring (Application Insights)
- [ ] Set up GitHub Actions for CI/CD
- [ ] Enable auto-scaling rules
- [ ] Move secrets to Azure Key Vault

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

