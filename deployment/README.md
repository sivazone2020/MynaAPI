# MynaAPI Azure Deployment Guide

This guide provides comprehensive instructions for deploying the MynaAPI to Azure Container Apps using Infrastructure as Code (IaC) and CI/CD pipelines.

## 🏗️ Architecture Overview

The deployment creates the following Azure resources:

- **Azure Container Registry (ACR)**: Stores Docker images
- **Azure Container Apps**: Hosts the application with auto-scaling
- **Azure Key Vault**: Securely stores API keys and secrets
- **Azure Log Analytics**: Centralized logging and monitoring
- **Application Insights**: Application performance monitoring
- **Managed Identity**: Secure access to Azure services

## 📋 Prerequisites

### Required Tools
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (latest version)
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (for local builds)
- [Git](https://git-scm.com/) (for version control)
- [PowerShell 7+](https://github.com/PowerShell/PowerShell) (for Windows scripts)

### Required Secrets
Before deployment, ensure you have the following:

- **OpenAI API Key**: For GPT-4 integration
- **Pinecone API Key**: For vector database access
- **Pinecone Host URL**: Your Pinecone service endpoint
- **JWT Secret Key**: For token authentication (generate a secure random string)

### Azure Subscription
- Subscription ID: `e584d9a6-2115-4a9b-a5d4-3d1948b95377`
- Required permissions: Contributor role on the subscription

## 🚀 Deployment Options

### Option 1: Automated CI/CD (Recommended)

The GitHub Actions workflow provides fully automated deployment with the following features:
- Automated testing and security scanning
- Multi-environment support (dev, staging, prod)
- Container image building and registry management
- Infrastructure deployment with ARM templates
- Post-deployment health checks

#### Setup GitHub Secrets

Add the following secrets to your GitHub repository:

```bash
# Repository -> Settings -> Secrets and variables -> Actions
AZURE_CREDENTIALS           # Azure service principal JSON
AZURE_ACR_USERNAME          # Container registry username
AZURE_ACR_PASSWORD          # Container registry password
OPENAI_API_KEY              # Your OpenAI API key
PINECONE_API_KEY            # Your Pinecone API key
PINECONE_HOST               # Your Pinecone host URL
JWT_SECRET_KEY              # Your JWT secret key
```

#### Azure Service Principal Setup

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac --name "mynaapi-github-actions" \
    --role contributor \
    --scopes /subscriptions/e584d9a6-2115-4a9b-a5d4-3d1948b95377 \
    --sdk-auth
```

Copy the JSON output to the `AZURE_CREDENTIALS` secret.

#### Trigger Deployment

1. **Automatic**: Push to `main` branch triggers production deployment
2. **Manual**: Use "Actions" tab -> "MynaAPI - Azure Container Apps Deployment" -> "Run workflow"

### Option 2: Manual Deployment Scripts

#### PowerShell Script (Windows)

```powershell
# Navigate to project directory
cd C:\Users\FusionGamingMasterPC\MynaAPI

# Deploy infrastructure
.\deployment\scripts\deploy.ps1 -Environment dev -Location eastus -Action deploy

# Build and push container image
.\deployment\scripts\deploy.ps1 -Environment dev -Location eastus -Action build

# Update container app
.\deployment\scripts\deploy.ps1 -Environment dev -Location eastus -Action update

# Or run full deployment
.\deployment\scripts\deploy.ps1 -Environment dev -Location eastus -Action full
```

#### Bash Script (Linux/macOS)

```bash
# Navigate to project directory
cd /path/to/MynaAPI

# Make script executable
chmod +x deployment/scripts/deploy.sh

# Deploy infrastructure
./deployment/scripts/deploy.sh dev eastus deploy

# Build and push container image
./deployment/scripts/deploy.sh dev eastus build

# Update container app
./deployment/scripts/deploy.sh dev eastus update

# Or run full deployment
./deployment/scripts/deploy.sh dev eastus full
```

### Option 3: Manual Azure CLI Commands

#### 1. Login and Set Subscription

```bash
az login
az account set --subscription e584d9a6-2115-4a9b-a5d4-3d1948b95377
```

#### 2. Create Resource Group

```bash
az group create --name mynaapi-dev-rg --location eastus
```

#### 3. Deploy Infrastructure

```bash
# Update parameters file with your secrets first
az deployment group create \
    --resource-group mynaapi-dev-rg \
    --template-file deployment/azure/main.json \
    --parameters @deployment/azure/parameters-dev.json
```

#### 4. Build and Push Container

```bash
# Get registry name
REGISTRY_NAME=$(az acr list --resource-group mynaapi-dev-rg --query "[0].name" --output tsv)

# Build image
docker build -t mynaapi:latest .

# Login to registry
az acr login --name $REGISTRY_NAME

# Tag and push
docker tag mynaapi:latest $REGISTRY_NAME.azurecr.io/mynaapi:latest
docker push $REGISTRY_NAME.azurecr.io/mynaapi:latest
```

#### 5. Update Container App

```bash
az containerapp update \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --image $REGISTRY_NAME.azurecr.io/mynaapi:latest
```

## 🔧 Configuration

### Environment-Specific Settings

#### Development Environment
- **Resource Group**: `mynaapi-dev-rg`
- **Resources**: 1 CPU, 2GB RAM
- **Scaling**: 1-3 instances
- **Cost**: ~$50-70/month

#### Production Environment
- **Resource Group**: `mynaapi-prod-rg`
- **Resources**: 2 CPU, 4GB RAM
- **Scaling**: 2-10 instances
- **Cost**: ~$100-300/month

### Secret Management

Secrets are stored securely in Azure Key Vault and accessed via Managed Identity:

```bash
# View secrets in Key Vault
az keyvault secret list --vault-name mynaapi-dev-kv

# Update a secret
az keyvault secret set --vault-name mynaapi-dev-kv \
    --name openai-api-key \
    --value "your-new-key"
```

### Environment Variables

The following environment variables are automatically configured:

| Variable | Description | Source |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Key Vault |
| `PINECONE_API_KEY` | Pinecone API key | Key Vault |
| `PINECONE_HOST` | Pinecone host URL | Parameters |
| `PINECONE_INDEX` | Pinecone index name | Parameters |
| `JWT_SECRET_KEY` | JWT signing key | Key Vault |
| `JWT_ALGORITHM` | JWT algorithm | Parameters |
| `LOG_LEVEL` | Logging level | Parameters |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | App Insights | Auto-generated |

## 📊 Monitoring and Logging

### Application Insights

Monitor application performance and errors:

```bash
# Get Application Insights connection string
az monitor app-insights component show \
    --app mynaapi-dev-ai \
    --resource-group mynaapi-dev-rg \
    --query connectionString
```

### Log Analytics

View application logs:

```bash
# Query logs
az monitor log-analytics query \
    --workspace mynaapi-dev-logs \
    --analytics-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(1h)"
```

### Health Checks

The application provides the following health endpoints:

- **Health Check**: `GET /health` - Basic application health
- **API Documentation**: `GET /docs` - Swagger UI
- **OpenAPI Spec**: `GET /openapi.json` - API specification

## 🔄 Scaling Configuration

### Auto-scaling Rules

The application automatically scales based on:

- **HTTP Requests**: Scales up when concurrent requests exceed 10
- **CPU Usage**: Scales up when CPU usage exceeds 70%
- **Memory Usage**: Scales up when memory usage exceeds 80%

### Manual Scaling

```bash
# Scale to specific number of replicas
az containerapp revision set-mode \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --mode single

az containerapp update \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --min-replicas 2 \
    --max-replicas 5
```

## 🛡️ Security

### Network Security

- **Private Endpoints**: Container apps run in isolated environments
- **HTTPS Only**: All traffic is encrypted with TLS 1.2+
- **Managed Identity**: No stored credentials for Azure service access

### Access Control

```bash
# Grant access to Key Vault
az keyvault set-policy \
    --name mynaapi-dev-kv \
    --object-id $(az identity show --name mynaapi-dev-identity --resource-group mynaapi-dev-rg --query principalId --output tsv) \
    --secret-permissions get list
```

### Security Scanning

The CI/CD pipeline includes:

- **Trivy**: Vulnerability scanning for containers
- **Code Scanning**: GitHub Advanced Security
- **Dependency Scanning**: Automated security updates

## 🔄 Updates and Rollbacks

### Rolling Updates

Container Apps supports zero-downtime deployments:

```bash
# Deploy new version
az containerapp update \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --image mynaapi-dev-acr.azurecr.io/mynaapi:v2.0.0
```

### Rollback

```bash
# List revisions
az containerapp revision list \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg

# Activate previous revision
az containerapp revision activate \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --revision mynaapi-dev-app--previous-revision-name
```

## 🧹 Cleanup

### Delete Specific Environment

```bash
# Delete development environment
az group delete --name mynaapi-dev-rg --yes --no-wait

# Delete production environment
az group delete --name mynaapi-prod-rg --yes --no-wait
```

### Cost Management

```bash
# View current costs
az consumption usage list \
    --subscription e584d9a6-2115-4a9b-a5d4-3d1948b95377 \
    --start-date 2024-01-01 \
    --end-date 2024-01-31
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Container App Not Starting

```bash
# Check container logs
az containerapp logs show \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --follow
```

#### 2. Key Vault Access Issues

```bash
# Verify managed identity permissions
az keyvault show \
    --name mynaapi-dev-kv \
    --query accessPolicies
```

#### 3. Image Pull Errors

```bash
# Check registry credentials
az acr credential show --name mynaapi-dev-acr
```

### Debug Commands

```bash
# Get container app details
az containerapp show \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg

# Check revision status
az containerapp revision list \
    --name mynaapi-dev-app \
    --resource-group mynaapi-dev-rg \
    --query "[].{Name:name,Active:properties.active,CreatedTime:properties.createdTime}"

# View deployment events
az deployment group list \
    --resource-group mynaapi-dev-rg \
    --query "[].{Name:name,State:properties.provisioningState,Timestamp:properties.timestamp}"
```

## 📞 Support

For deployment issues:

1. Check the [GitHub Actions logs](https://github.com/sivazone2020/MynaAPI/actions)
2. Review Azure portal logs in Application Insights
3. Verify all secrets are correctly configured
4. Ensure Azure CLI is properly authenticated

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://docs.microsoft.com/en-us/azure/container-apps/)
- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- [GitHub Actions for Azure](https://docs.microsoft.com/en-us/azure/developer/github/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
