# Simple script to build and push Docker images to Azure Container Registry
# Usage: .\build-and-push.ps1 -AcrName <your-acr> [-ImageVersion 1.2]

param(
    [Parameter(Mandatory)][string]$AcrName,  # ACR name without .azurecr.io
    [string]$ImageVersion = "1.2"            # Increment this for new versions
)
$ACR_NAME = $AcrName
$IMAGE_VERSION = $ImageVersion

# Derived variables
$ACR_LOGIN_SERVER = "${ACR_NAME}.azurecr.io"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SparkAI Docker Build & Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ACR: $ACR_LOGIN_SERVER" -ForegroundColor Yellow
Write-Host "Version: $IMAGE_VERSION" -ForegroundColor Yellow
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not running. Please start it first." -ForegroundColor Red
    exit 1
}

# Step 1: Login to ACR
Write-Host ""
Write-Host "Step 1: Logging into Azure Container Registry..." -ForegroundColor Cyan
az acr login --name $ACR_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to login to ACR. Make sure you're logged into Azure CLI (run 'az login')" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Successfully logged into ACR" -ForegroundColor Green

# Step 2: Build Backend Image
Write-Host ""
Write-Host "Step 2: Building Backend Docker Image..." -ForegroundColor Cyan
docker build -t sparkai-backend:${IMAGE_VERSION} -f Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to build backend image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend image built successfully" -ForegroundColor Green

# Step 3: Tag Backend Image
Write-Host ""
Write-Host "Step 3: Tagging Backend Image..." -ForegroundColor Cyan
docker tag sparkai-backend:${IMAGE_VERSION} ${ACR_LOGIN_SERVER}/sparkai-backend:${IMAGE_VERSION}
docker tag sparkai-backend:${IMAGE_VERSION} ${ACR_LOGIN_SERVER}/sparkai-backend:latest
Write-Host "✓ Backend image tagged" -ForegroundColor Green

# Step 4: Push Backend Image
Write-Host ""
Write-Host "Step 4: Pushing Backend Image to ACR..." -ForegroundColor Cyan
docker push ${ACR_LOGIN_SERVER}/sparkai-backend:${IMAGE_VERSION}
docker push ${ACR_LOGIN_SERVER}/sparkai-backend:latest
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to push backend image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend image pushed successfully" -ForegroundColor Green

# Step 5: Build Frontend Image
Write-Host ""
Write-Host "Step 5: Building Frontend Docker Image..." -ForegroundColor Cyan
docker build -t sparkai-frontend:${IMAGE_VERSION} -f Dockerfile.streamlit .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to build frontend image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Frontend image built successfully" -ForegroundColor Green

# Step 6: Tag Frontend Image
Write-Host ""
Write-Host "Step 6: Tagging Frontend Image..." -ForegroundColor Cyan
docker tag sparkai-frontend:${IMAGE_VERSION} ${ACR_LOGIN_SERVER}/sparkai-frontend:${IMAGE_VERSION}
docker tag sparkai-frontend:${IMAGE_VERSION} ${ACR_LOGIN_SERVER}/sparkai-frontend:latest
Write-Host "✓ Frontend image tagged" -ForegroundColor Green

# Step 7: Push Frontend Image
Write-Host ""
Write-Host "Step 7: Pushing Frontend Image to ACR..." -ForegroundColor Cyan
docker push ${ACR_LOGIN_SERVER}/sparkai-frontend:${IMAGE_VERSION}
docker push ${ACR_LOGIN_SERVER}/sparkai-frontend:latest
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to push frontend image" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Frontend image pushed successfully" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ All Images Built and Pushed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Images in ACR:" -ForegroundColor Yellow
Write-Host "  Backend:  ${ACR_LOGIN_SERVER}/sparkai-backend:${IMAGE_VERSION}" -ForegroundColor Cyan
Write-Host "  Backend:  ${ACR_LOGIN_SERVER}/sparkai-backend:latest" -ForegroundColor Cyan
Write-Host "  Frontend: ${ACR_LOGIN_SERVER}/sparkai-frontend:${IMAGE_VERSION}" -ForegroundColor Cyan
Write-Host "  Frontend: ${ACR_LOGIN_SERVER}/sparkai-frontend:latest" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Deploy to Azure Container Apps using the Azure Portal or CLI" -ForegroundColor White
Write-Host "2. Set environment variables for the backend" -ForegroundColor White
Write-Host "3. Configure the frontend to point to the backend URL" -ForegroundColor White
Write-Host ""

