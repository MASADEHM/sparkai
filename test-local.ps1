# Test the application locally using Docker Compose
# Usage: .\test-local.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing SparkAI Locally" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create a .env file with your Azure OpenAI credentials:" -ForegroundColor Yellow
    Write-Host "AZURE_OPENAI_ENDPOINT=your_azure_endpoint" -ForegroundColor White
    Write-Host "OPENAI_API_KEY=your_api_key" -ForegroundColor White
    Write-Host "AZURE_OPENAI_CHAT_MODEL=your_chat_model" -ForegroundColor White
    Write-Host "AZURE_OPENAI_EMEBDDING_DEPLOYMENT=your_embedding_deployment" -ForegroundColor White
    Write-Host "AZURE_OPENAI_EMEBDDING_MODEL=your_embedding_model" -ForegroundColor White
    Write-Host "AZURE_OPENAI_API_EMEBDDING_VERSION=your_api_version" -ForegroundColor White
    exit 1
}

# Check if Docker is running
Write-Host "Checking Docker Desktop..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not running. Please start it first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting services with Docker Compose..." -ForegroundColor Cyan
docker-compose up --build

Write-Host ""
Write-Host "To stop the services, press Ctrl+C" -ForegroundColor Yellow

