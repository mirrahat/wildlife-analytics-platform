# Azure Deployment Instructions for Wildlife Analytics Platform
# Account: mirrahat0081@outlook.com
# Subscription: Azure for Students (b6a34c6e-3b3b-4cf4-85dc-279699bca03c)
# Resource Group: rg-user-rahat
# Location: Australia East

## 🚀 STEP-BY-STEP DEPLOYMENT GUIDE

### Option 1: Azure Portal Deployment (Recommended)

1. **Go to Azure Portal**
   - Open: https://portal.azure.com
   - Login with: mirrahat0081@outlook.com

2. **Deploy Template**
   - Click "Create a resource"
   - Search for "Template deployment (deploy using custom templates)"
   - Click "Create"

3. **Upload Template**
   - Click "Build your own template in the editor"
   - Click "Load file" and select: azure-deploy-template.json
   - Click "Save"

4. **Configure Deployment**
   - Subscription: Azure for Students
   - Resource Group: rg-user-rahat
   - Region: Australia East
   - Web App Name: wildlife-analytics-rahat (or your preference)
   - SKU: B1 (Basic) or F1 (Free tier)

5. **Deploy**
   - Click "Review + create"
   - Click "Create"
   - Wait 5-10 minutes for deployment

### Option 2: Create App Service Manually

1. **Create Web App**
   - Go to: https://portal.azure.com
   - Click "Create a resource" → "Web App"
   
2. **Basic Settings**
   - Subscription: Azure for Students
   - Resource Group: rg-user-rahat
   - Name: wildlife-analytics-rahat
   - Publish: Code
   - Runtime Stack: Python 3.11
   - Operating System: Linux
   - Region: Australia East
   - App Service Plan: Create new (B1 Basic or F1 Free)

3. **Deployment Settings**
   - Go to your created Web App
   - Click "Deployment Center" in left menu
   - Source: External Git
   - Repository: https://github.com/mirrahat/wildlife-analytics-platform
   - Branch: dev
   - Click "Save"

4. **Configuration**
   - Go to "Configuration" in left menu
   - Click "General settings"
   - Startup Command: python -m streamlit run streamlit_dashboard.py --server.port=8000 --server.address=0.0.0.0 --server.headless=true
   - Click "Save"

### 🌐 Your App URLs:
- Production: https://wildlife-analytics-rahat.azurewebsites.net
- Or: https://[your-app-name].azurewebsites.net

### 📋 App Settings to Add (if needed):
- SCM_DO_BUILD_DURING_DEPLOYMENT = true
- STREAMLIT_SERVER_PORT = 8000
- STREAMLIT_SERVER_ADDRESS = 0.0.0.0
- STREAMLIT_SERVER_HEADLESS = true

## ✅ Expected Result:
Your Australian Wildlife Analytics Platform will be live with:
- ✅ Real-time data visualization
- ✅ ETL pipeline functionality
- ✅ Interactive species exploration
- ✅ Data quality dashboard
- ✅ All features from local version