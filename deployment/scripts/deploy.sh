#!/bin/bash

# MynaAPI Azure Deployment Script
# This script deploys the MynaAPI to Azure Container Apps

set -e  # Exit on any error

# Configuration
SUBSCRIPTION_ID="e584d9a6-2115-4a9b-a5d4-3d1948b95377"
PROJECT_NAME="mynaapi"
ENVIRONMENT="${1:-dev}"  # Default to dev if no environment specified
LOCATION="${2:-eastus}"   # Default to East US if no location specified
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation functions
validate_environment() {
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        log_error "Invalid environment: $ENVIRONMENT. Must be dev, staging, or prod."
        exit 1
    fi
}

validate_azure_cli() {
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi
}

check_azure_login() {
    log_info "Checking Azure CLI login status..."
    if ! az account show &> /dev/null; then
        log_warning "Not logged into Azure. Please login first."
        az login
    fi
    
    # Set the subscription
    log_info "Setting Azure subscription to: $SUBSCRIPTION_ID"
    az account set --subscription "$SUBSCRIPTION_ID"
}

# Main deployment function
deploy_infrastructure() {
    local template_file="deployment/azure/main.json"
    local parameters_file="deployment/azure/parameters-${ENVIRONMENT}.json"
    
    log_info "Starting deployment for environment: $ENVIRONMENT"
    log_info "Resource Group: $RESOURCE_GROUP"
    log_info "Location: $LOCATION"
    
    # Check if template files exist
    if [[ ! -f "$template_file" ]]; then
        log_error "Template file not found: $template_file"
        exit 1
    fi
    
    if [[ ! -f "$parameters_file" ]]; then
        log_error "Parameters file not found: $parameters_file"
        exit 1
    fi
    
    # Create resource group if it doesn't exist
    log_info "Creating resource group: $RESOURCE_GROUP"
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --subscription "$SUBSCRIPTION_ID"
    
    # Deploy the ARM template
    log_info "Deploying ARM template..."
    deployment_name="${PROJECT_NAME}-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
    
    az deployment group create \
        --resource-group "$RESOURCE_GROUP" \
        --template-file "$template_file" \
        --parameters "@$parameters_file" \
        --name "$deployment_name" \
        --subscription "$SUBSCRIPTION_ID" \
        --verbose
    
    # Get deployment outputs
    log_info "Retrieving deployment outputs..."
    container_app_url=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$deployment_name" \
        --query "properties.outputs.containerAppUrl.value" \
        --output tsv)
    
    container_registry=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$deployment_name" \
        --query "properties.outputs.containerRegistryLoginServer.value" \
        --output tsv)
    
    keyvault_name=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "$deployment_name" \
        --query "properties.outputs.keyVaultName.value" \
        --output tsv)
    
    log_success "Deployment completed successfully!"
    echo ""
    echo "=== Deployment Summary ==="
    echo "Environment: $ENVIRONMENT"
    echo "Resource Group: $RESOURCE_GROUP"
    echo "Container App URL: $container_app_url"
    echo "Container Registry: $container_registry"
    echo "Key Vault: $keyvault_name"
    echo ""
    echo "=== Next Steps ==="
    echo "1. Build and push your container image to: $container_registry"
    echo "2. Update the container app with your image"
    echo "3. Configure secrets in Key Vault: $keyvault_name"
    echo "4. Test your application at: $container_app_url"
}

# Build and push container image
build_and_push_image() {
    local registry_name=$(az acr list \
        --resource-group "$RESOURCE_GROUP" \
        --query "[0].name" \
        --output tsv)
    
    if [[ -z "$registry_name" ]]; then
        log_error "Container registry not found in resource group: $RESOURCE_GROUP"
        exit 1
    fi
    
    local registry_server="${registry_name}.azurecr.io"
    local image_name="${PROJECT_NAME}:latest"
    local full_image_name="${registry_server}/${image_name}"
    
    log_info "Building Docker image: $image_name"
    docker build -t "$image_name" .
    
    log_info "Logging into Azure Container Registry: $registry_server"
    az acr login --name "$registry_name"
    
    log_info "Tagging image for registry: $full_image_name"
    docker tag "$image_name" "$full_image_name"
    
    log_info "Pushing image to registry: $full_image_name"
    docker push "$full_image_name"
    
    log_success "Image pushed successfully: $full_image_name"
}

# Update container app with new image
update_container_app() {
    local container_app_name="${PROJECT_NAME}-${ENVIRONMENT}-app"
    local registry_name=$(az acr list \
        --resource-group "$RESOURCE_GROUP" \
        --query "[0].name" \
        --output tsv)
    
    local registry_server="${registry_name}.azurecr.io"
    local image_name="${PROJECT_NAME}:latest"
    local full_image_name="${registry_server}/${image_name}"
    
    log_info "Updating container app: $container_app_name"
    log_info "New image: $full_image_name"
    
    az containerapp update \
        --name "$container_app_name" \
        --resource-group "$RESOURCE_GROUP" \
        --image "$full_image_name"
    
    log_success "Container app updated successfully!"
}

# Main script execution
main() {
    echo "=== MynaAPI Azure Deployment Script ==="
    echo "Environment: $ENVIRONMENT"
    echo "Location: $LOCATION"
    echo ""
    
    validate_environment
    validate_azure_cli
    check_azure_login
    
    case "${3:-deploy}" in
        "deploy")
            deploy_infrastructure
            ;;
        "build")
            build_and_push_image
            ;;
        "update")
            update_container_app
            ;;
        "full")
            deploy_infrastructure
            build_and_push_image
            update_container_app
            ;;
        *)
            echo "Usage: $0 [environment] [location] [action]"
            echo "  environment: dev, staging, prod (default: dev)"
            echo "  location: Azure region (default: eastus)"
            echo "  action: deploy, build, update, full (default: deploy)"
            echo ""
            echo "Examples:"
            echo "  $0 dev eastus deploy     # Deploy infrastructure only"
            echo "  $0 dev eastus build      # Build and push container image"
            echo "  $0 dev eastus update     # Update container app with new image"
            echo "  $0 dev eastus full       # Full deployment (infrastructure + container)"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
