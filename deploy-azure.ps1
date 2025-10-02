# Azure Deployment Script for Wildlife Analytics Platform
# Deploy directly from GitHub repository

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-wildlife-analytics",
    
    [Parameter(Mandatory=$false)]
    [string]$AppName = "wildlife-analytics-rahat",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US"
)

Write-Host "🚀 Deploying Wildlife Analytics Platform to Azure..." -ForegroundColor Green
Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "   Subscription ID: $SubscriptionId"
Write-Host "   Resource Group: $ResourceGroupName"
Write-Host "   App Name: $AppName"
Write-Host "   Location: $Location"
Write-Host "   GitHub Repo: https://github.com/mirrahat/wildlife-analytics-platform"
Write-Host ""

# Create Azure Resource Manager Template JSON file directly
$templateJson = @'
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "webAppName": {
      "type": "string",
      "defaultValue": "wildlife-analytics-rahat"
    },
    "location": {
      "type": "string",
      "defaultValue": "East US"
    }
  },
  "variables": {
    "appServicePlanName": "[concat(parameters('webAppName'), '-plan')]"
  },
  "resources": [
    {
      "type": "Microsoft.Web/serverfarms",
      "apiVersion": "2021-02-01",
      "name": "[variables('appServicePlanName')]",
      "location": "[parameters('location')]",
      "sku": {
        "name": "B1"
      },
      "kind": "linux",
      "properties": {
        "reserved": true
      }
    },
    {
      "type": "Microsoft.Web/sites",
      "apiVersion": "2021-02-01",
      "name": "[parameters('webAppName')]",
      "location": "[parameters('location')]",
      "dependsOn": [
        "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]"
      ],
      "properties": {
        "serverFarmId": "[resourceId('Microsoft.Web/serverfarms', variables('appServicePlanName'))]",
        "siteConfig": {
          "linuxFxVersion": "PYTHON|3.11",
          "appCommandLine": "python -m streamlit run streamlit_dashboard.py --server.port=8000 --server.address=0.0.0.0 --server.headless=true",
          "appSettings": [
            {
              "name": "SCM_DO_BUILD_DURING_DEPLOYMENT",
              "value": "true"
            },
            {
              "name": "STREAMLIT_SERVER_PORT",
              "value": "8000"
            },
            {
              "name": "STREAMLIT_SERVER_ADDRESS",
              "value": "0.0.0.0"
            },
            {
              "name": "STREAMLIT_SERVER_HEADLESS",
              "value": "true"
            }
          ]
        }
      }
    },
    {
      "type": "Microsoft.Web/sites/sourcecontrols",
      "apiVersion": "2021-02-01",
      "name": "[concat(parameters('webAppName'), '/web')]",
      "dependsOn": [
        "[resourceId('Microsoft.Web/sites', parameters('webAppName'))]"
      ],
      "properties": {
        "repoUrl": "https://github.com/mirrahat/wildlife-analytics-platform",
        "branch": "dev",
        "isManualIntegration": true
      }
    }
  ],
  "outputs": {
    "webAppUrl": {
      "type": "string",
      "value": "[concat('https://', parameters('webAppName'), '.azurewebsites.net')]"
    }
  }
}
'@

# Save template to file
$templateJson | Out-File -FilePath "azure-deploy-template.json" -Encoding UTF8

Write-Host "✅ Template created: azure-deploy-template.json" -ForegroundColor Green
Write-Host ""
Write-Host "🔹 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Go to Azure Portal: https://portal.azure.com" -ForegroundColor White
Write-Host "2. Create Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "3. Deploy Template:" -ForegroundColor White
Write-Host "   • Click 'Create a resource' → 'Template deployment'" -ForegroundColor Gray
Write-Host "   • Upload the azure-deploy-template.json file" -ForegroundColor Gray
Write-Host "   • Fill in parameters and deploy" -ForegroundColor Gray
Write-Host ""
Write-Host "🔹 OR use Azure CLI (if working):" -ForegroundColor Cyan
Write-Host "az group create --name $ResourceGroupName --location '$Location'" -ForegroundColor Gray
Write-Host "az deployment group create --resource-group $ResourceGroupName --template-file azure-deploy-template.json" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 Your app will be available at: https://$AppName.azurewebsites.net" -ForegroundColor Green
