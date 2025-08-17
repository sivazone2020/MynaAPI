# MynaAPI Azure Deployment PowerShell Script
# This script deploys the MynaAPI to Azure Container Apps

param(
    [Parameter(Position=0)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Position=1)]
    [string]$Location = "eastus",
    
    [Parameter(Position=2)]
    [ValidateSet("deploy", "build", "update", "full")]
    [string]$Action = "deploy"
)

# Configuration
$SubscriptionId = "e584d9a6-2115-4a9b-a5d4-3d1948b95377"
$ProjectName = "mynaapi"
$ResourceGroup = "$ProjectName-$Environment-rg"

# Error handling
$ErrorActionPreference = "Stop"

# Logging functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Validation functions
function Test-AzureCLI {
    try {
        $null = Get-Command az -ErrorAction Stop
        Write-Info "Azure CLI found"
    }
    catch {
        Write-Error "Azure CLI is not installed. Please install it first."
        Write-Host "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    }
}

function Test-AzureLogin {
    Write-Info "Checking Azure CLI login status..."
    
    try {
        $account = az account show 2>$null | ConvertFrom-Json
        if (-not $account) {
            throw "Not logged in"
        }
        Write-Info "Already logged into Azure as: $($account.user.name)"
    }
    catch {
        Write-Warning "Not logged into Azure. Please login first."
        az login
    }
    
    # Set the subscription
    Write-Info "Setting Azure subscription to: $SubscriptionId"
    az account set --subscription $SubscriptionId
}

function Test-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
        Write-Info "Docker found"
    }
    catch {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        Write-Host "Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    }
}

# Main deployment function
function Deploy-Infrastructure {
    $templateFile = "deployment\azure\main.json"
    $parametersFile = "deployment\azure\parameters-$Environment.json"
    
    Write-Info "Starting deployment for environment: $Environment"
    Write-Info "Resource Group: $ResourceGroup"
    Write-Info "Location: $Location"
    
    # Check if template files exist
    if (-not (Test-Path $templateFile)) {
        Write-Error "Template file not found: $templateFile"
        exit 1
    }
    
    if (-not (Test-Path $parametersFile)) {
        Write-Error "Parameters file not found: $parametersFile"
        exit 1
    }
    
    # Create resource group if it doesn't exist
    Write-Info "Creating resource group: $ResourceGroup"
    az group create --name $ResourceGroup --location $Location --subscription $SubscriptionId
    
    # Deploy the ARM template
    Write-Info "Deploying ARM template..."
    $deploymentName = "$ProjectName-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    
    az deployment group create `
        --resource-group $ResourceGroup `
        --template-file $templateFile `
        --parameters "@$parametersFile" `
        --name $deploymentName `
        --subscription $SubscriptionId `
        --verbose
    
    # Get deployment outputs
    Write-Info "Retrieving deployment outputs..."
    $containerAppUrl = az deployment group show `
        --resource-group $ResourceGroup `
        --name $deploymentName `
        --query "properties.outputs.containerAppUrl.value" `
        --output tsv
    
    $containerRegistry = az deployment group show `
        --resource-group $ResourceGroup `
        --name $deploymentName `
        --query "properties.outputs.containerRegistryLoginServer.value" `
        --output tsv
    
    $keyVaultName = az deployment group show `
        --resource-group $ResourceGroup `
        --name $deploymentName `
        --query "properties.outputs.keyVaultName.value" `
        --output tsv
    
    Write-Success "Deployment completed successfully!"
    Write-Host ""
    Write-Host "=== Deployment Summary ===" -ForegroundColor Cyan
    Write-Host "Environment: $Environment"
    Write-Host "Resource Group: $ResourceGroup"
    Write-Host "Container App URL: $containerAppUrl"
    Write-Host "Container Registry: $containerRegistry"
    Write-Host "Key Vault: $keyVaultName"
    Write-Host ""
    Write-Host "=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Build and push your container image to: $containerRegistry"
    Write-Host "2. Update the container app with your image"
    Write-Host "3. Configure secrets in Key Vault: $keyVaultName"
    Write-Host "4. Test your application at: $containerAppUrl"
}

# Build and push container image
function Build-AndPushImage {
    $registryName = az acr list --resource-group $ResourceGroup --query "[0].name" --output tsv
    
    if (-not $registryName) {
        Write-Error "Container registry not found in resource group: $ResourceGroup"
        exit 1
    }
    
    $registryServer = "$registryName.azurecr.io"
    $imageName = "$ProjectName`:latest"
    $fullImageName = "$registryServer/$imageName"
    
    Write-Info "Building Docker image: $imageName"
    docker build -t $imageName .
    
    Write-Info "Logging into Azure Container Registry: $registryServer"
    az acr login --name $registryName
    
    Write-Info "Tagging image for registry: $fullImageName"
    docker tag $imageName $fullImageName
    
    Write-Info "Pushing image to registry: $fullImageName"
    docker push $fullImageName
    
    Write-Success "Image pushed successfully: $fullImageName"
}

# Update container app with new image
function Update-ContainerApp {
    $containerAppName = "$ProjectName-$Environment-app"
    $registryName = az acr list --resource-group $ResourceGroup --query "[0].name" --output tsv
    
    $registryServer = "$registryName.azurecr.io"
    $imageName = "$ProjectName`:latest"
    $fullImageName = "$registryServer/$imageName"
    
    Write-Info "Updating container app: $containerAppName"
    Write-Info "New image: $fullImageName"
    
    az containerapp update `
        --name $containerAppName `
        --resource-group $ResourceGroup `
        --image $fullImageName
    
    Write-Success "Container app updated successfully!"
}

# Main script execution
function Main {
    Write-Host "=== MynaAPI Azure Deployment Script ===" -ForegroundColor Cyan
    Write-Host "Environment: $Environment"
    Write-Host "Location: $Location"
    Write-Host "Action: $Action"
    Write-Host ""
    
    Test-AzureCLI
    Test-AzureLogin
    
    switch ($Action) {
        "deploy" {
            Deploy-Infrastructure
        }
        "build" {
            Test-Docker
            Build-AndPushImage
        }
        "update" {
            Update-ContainerApp
        }
        "full" {
            Test-Docker
            Deploy-Infrastructure
            Build-AndPushImage
            Update-ContainerApp
        }
    }
}

# Run main function
try {
    Main
}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    exit 1
}
