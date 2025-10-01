#!/bin/bash

# 🚀 Quick Azure Deployment Script for Australian Wildlife Analytics Platform
# Developed by Mir Hasibul Hasan Rahat

echo "🇦🇺 Deploying Australian Wildlife Analytics Platform to Azure..."

# Configuration
RESOURCE_GROUP="wildlife-analytics-rg"
APP_SERVICE_PLAN="wildlife-analytics-plan"
WEB_APP_NAME="wildlife-analytics-app-$(date +%s)"
LOCATION="eastus"
SKU="B1"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure
echo "🔐 Logging into Azure..."
az login

# Create resource group
echo "📦 Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service plan
echo "⚙️ Creating App Service plan: $APP_SERVICE_PLAN"
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux

# Create Web App
echo "🌐 Creating Web App: $WEB_APP_NAME"
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --runtime "PYTHON|3.9" \
    --deployment-local-git

# Configure startup command
echo "🔧 Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --startup-file "startup.sh"

# Set application settings
echo "⚙️ Setting application configuration..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        STREAMLIT_SERVER_HEADLESS=true \
        STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
        STREAMLIT_SERVER_PORT=8000

# Get deployment credentials
echo "🔑 Getting deployment credentials..."
DEPLOYMENT_URL=$(az webapp deployment source config-local-git \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query url -o tsv)

echo "📝 Deployment configured successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Add Azure as a remote repository:"
echo "   git remote add azure $DEPLOYMENT_URL"
echo ""
echo "2. Deploy your code:"
echo "   git push azure main"
echo ""
echo "3. Your app will be available at:"
echo "   https://$WEB_APP_NAME.azurewebsites.net"
echo ""
echo "📊 Monitor your app:"
echo "   az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "🗑️ To delete resources when done:"
echo "   az group delete --name $RESOURCE_GROUP --yes --no-wait"
echo ""
echo "✅ Azure deployment setup complete! 🇦🇺🦘"