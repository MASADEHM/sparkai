# 🚀 SparkAI - Quick Deployment Guide

## 3-Step Deployment with Docker Desktop

### ✅ Prerequisites
- [ ] Docker Desktop installed and running
- [ ] Azure CLI installed (`az --version` to check)
- [ ] Logged into Azure (`az login`)
- [ ] `.env` file created from [.env.example](.env.example)

---

### 📦 Step 1: Test Locally (Optional)

```bash
docker compose up --build
```
- Opens at: http://localhost:8501
- Press `Ctrl+C` to stop

---

### 🏗️ Step 2: Build & Push to ACR

```powershell
.\build-and-push.ps1 -AcrName <your-acr> -ImageVersion 1.2
```

This builds and pushes:
- `<your-acr>.azurecr.io/sparkai-backend:1.2`
- `<your-acr>.azurecr.io/sparkai-frontend:1.2`

---

### ☁️ Step 3: Deploy to Azure

1. Go to [portal.azure.com](https://portal.azure.com)
2. Create a Container Apps Environment
3. Create 2 Container Apps:
   - **Backend**: `<your-acr>.azurecr.io/sparkai-backend:latest` (port 8000)
   - **Frontend**: `<your-acr>.azurecr.io/sparkai-frontend:latest` (port 8501)
4. Set the variables from `.env` on the backend
5. Set `API_URL` on the frontend to the backend URL, plus the same `API_USERNAME` / `API_PASSWORD` as the backend

---

## 🔧 Update Existing Deployment

When you make code changes:

```powershell
# 1. Build and push a new version
.\build-and-push.ps1 -AcrName <your-acr> -ImageVersion 1.3

# 2. Update the Azure Container Apps
az containerapp update --name sparkai-backend --resource-group <your-resource-group> --image <your-acr>.azurecr.io/sparkai-backend:1.3
az containerapp update --name sparkai-frontend --resource-group <your-resource-group> --image <your-acr>.azurecr.io/sparkai-frontend:1.3
```

---

## 🔍 Useful Commands

```bash
# View Azure logs
az containerapp logs show --name sparkai-backend --resource-group <your-resource-group> --follow

# Stop local services
docker compose down

# List ACR images
az acr repository list --name <your-acr> --output table
az acr repository show-tags --name <your-acr> --repository sparkai-backend --output table
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Docker not running | Start Docker Desktop |
| ACR login fails | Run `az login` again |
| Build fails | Check the `.env` file exists |
| Port 8000/8501 in use | Stop other services or change ports |
| Container not starting | Check logs with `docker logs <container-id>` |

---

## 📂 Deployment Files

| File | Purpose |
|------|---------|
| `build-and-push.ps1` | Build & push images to ACR |
| `docker-compose.yml` | Local multi-container setup |
| `Dockerfile` | Backend container |
| `Dockerfile.streamlit` | Frontend container |
| `.dockerignore` | Files to exclude from images |

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
