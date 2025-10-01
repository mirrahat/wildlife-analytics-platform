# 🚀 Azure Deployment Guide
# Australian Wildlife Analytics Platform

## 📋 Prerequisites

1. **Azure Account**: Sign up at https://azure.microsoft.com/free/
2. **Azure CLI**: Install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
3. **Git**: Ensure your project is in a Git repository

## 🌐 Deployment Options

### Option 1: Azure App Service (Recommended)

#### Step 1: Login to Azure
```bash
az login
```

#### Step 2: Create Resource Group
```bash
az group create --name wildlife-analytics-rg --location eastus
```

#### Step 3: Create App Service Plan
```bash
az appservice plan create --name wildlife-analytics-plan --resource-group wildlife-analytics-rg --sku B1 --is-linux
```

#### Step 4: Create Web App
```bash
az webapp create --resource-group wildlife-analytics-rg --plan wildlife-analytics-plan --name wildlife-analytics-app --runtime "PYTHON|3.9" --deployment-local-git
```

#### Step 5: Configure Startup Command
```bash
az webapp config set --resource-group wildlife-analytics-rg --name wildlife-analytics-app --startup-file "startup.sh"
```

#### Step 6: Deploy from Git
```bash
# Add Azure remote
az webapp deployment source config-local-git --name wildlife-analytics-app --resource-group wildlife-analytics-rg

# Get deployment URL
az webapp deployment list-publishing-credentials --name wildlife-analytics-app --resource-group wildlife-analytics-rg

# Push to Azure
git remote add azure <deployment-url>
git push azure main
```

### Option 2: Azure Container Instances

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 2: Build and Deploy Container
```bash
# Build image
docker build -t wildlife-analytics .

# Create Azure Container Registry
az acr create --resource-group wildlife-analytics-rg --name wildlifeacr --sku Basic

# Push to ACR
az acr build --registry wildlifeacr --image wildlife-analytics .

# Deploy to Container Instances
az container create --resource-group wildlife-analytics-rg --name wildlife-analytics-container --image wildlifeacr.azurecr.io/wildlife-analytics --dns-name-label wildlife-analytics --ports 8501
```

### Option 3: GitHub Actions (CI/CD)

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'wildlife-analytics-app'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## ⚙️ Environment Configuration

### App Service Settings
```bash
# Set environment variables
az webapp config appsettings set --resource-group wildlife-analytics-rg --name wildlife-analytics-app --settings \
  STREAMLIT_SERVER_HEADLESS=true \
  STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  STREAMLIT_SERVER_PORT=8000
```

### Database Configuration
The app uses SQLite for simplicity, but for production consider:
- Azure Database for PostgreSQL
- Azure Cosmos DB
- Azure SQL Database

## 🔧 Post-Deployment Steps

1. **Custom Domain** (Optional):
```bash
az webapp config hostname add --webapp-name wildlife-analytics-app --resource-group wildlife-analytics-rg --hostname yourdomain.com
```

2. **SSL Certificate**:
```bash
az webapp config ssl bind --certificate-thumbprint <thumbprint> --ssl-type SNI --name wildlife-analytics-app --resource-group wildlife-analytics-rg
```

3. **Application Insights**:
```bash
az monitor app-insights component create --app wildlife-analytics-insights --location eastus --resource-group wildlife-analytics-rg
```

## 📊 Monitoring & Scaling

### Enable Application Insights
```bash
az webapp config appsettings set --resource-group wildlife-analytics-rg --name wildlife-analytics-app --settings \
  APPINSIGHTS_INSTRUMENTATIONKEY=<your-key>
```

### Auto-scaling
```bash
az monitor autoscale create --resource-group wildlife-analytics-rg --resource /subscriptions/<subscription-id>/resourceGroups/wildlife-analytics-rg/providers/Microsoft.Web/serverfarms/wildlife-analytics-plan --min-count 1 --max-count 5 --count 1
```

## 🌍 Access Your Deployed App

After successful deployment, your app will be available at:
- **App Service**: `https://wildlife-analytics-app.azurewebsites.net`
- **Container Instance**: `http://wildlife-analytics.eastus.azurecontainer.io:8501`

## 🔍 Troubleshooting

### View logs:
```bash
az webapp log tail --name wildlife-analytics-app --resource-group wildlife-analytics-rg
```

### SSH into container:
```bash
az webapp ssh --name wildlife-analytics-app --resource-group wildlife-analytics-rg
```

## 💰 Cost Optimization

- Use **B1 Basic** plan for development ($13.14/month)
- Use **P1V2 Premium** for production ($73/month)
- Enable auto-scaling to handle traffic spikes
- Consider Azure Free Tier limitations

## 🚀 Quick Deploy Commands

```bash
# Complete deployment in one go
az group create --name wildlife-analytics-rg --location eastus
az appservice plan create --name wildlife-analytics-plan --resource-group wildlife-analytics-rg --sku B1 --is-linux
az webapp create --resource-group wildlife-analytics-rg --plan wildlife-analytics-plan --name wildlife-analytics-app-$(date +%s) --runtime "PYTHON|3.9" --deployment-local-git
az webapp config set --resource-group wildlife-analytics-rg --name wildlife-analytics-app-$(date +%s) --startup-file "startup.sh"
```

## 📞 Support

For deployment issues:
- Check Azure docs: https://docs.microsoft.com/azure/app-service/
- Azure support: https://azure.microsoft.com/support/
- Streamlit on Azure: https://docs.streamlit.io/knowledge-base/deploy/azure

---

**🇦🇺 Australian Wildlife Analytics Platform - Ready for Global Access! 🦘**