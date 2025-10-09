# Databricks Setup Script for Capstone Project
#
# IMPORTANT: This script reads credentials from ~/.databrickscfg
# Ensure you have configured Databricks CLI before running this script.
#
# Load credentials from .databrickscfg
$ConfigPath = "$env:USERPROFILE\.databrickscfg"
if (Test-Path $ConfigPath) {
    $config = Get-Content $ConfigPath
    $env:DATABRICKS_HOST = ($config | Select-String "host = (.*)").Matches.Groups[1].Value
    $env:DATABRICKS_TOKEN = ($config | Select-String "token = (.*)").Matches.Groups[1].Value
} else {
    Write-Error "Databricks config not found at $ConfigPath"
    exit 1
}

$DB = "C:\Users\Diaa\AppData\Roaming\Python\Python313\Scripts\databricks.exe"

Write-Host "===== Databricks Capstone Project Setup =====" -ForegroundColor Cyan
Write-Host ""

# 1. Upload Dataset to DBFS
Write-Host "[1/4] Uploading dataset files to DBFS..." -ForegroundColor Yellow
& $DB fs mkdirs dbfs:/FileStore/capstone/test_data
& $DB fs cp --recursive "CapstoneProject/Capstone Project/Data Set/" dbfs:/FileStore/capstone/test_data/ --overwrite

Write-Host "[1/4] Dataset upload complete!" -ForegroundColor Green
Write-Host ""

# 2. Import Notebooks to Workspace
Write-Host "[2/4] Importing notebooks to workspace..." -ForegroundColor Yellow
& $DB workspace mkdirs /Users/omaressamrme@outlook.com/capstone
& $DB workspace import_dir --overwrite "CapstoneProject/Capstone Project/Notebooks" /Users/omaressamrme@outlook.com/capstone/

Write-Host "[2/4] Notebooks imported!" -ForegroundColor Green
Write-Host ""

# 3. Create External Locations (Unity Catalog)
Write-Host "[3/4] Setting up external storage locations..." -ForegroundColor Yellow
Write-Host "Note: External locations require cloud storage (Azure ADLS/S3)" -ForegroundColor Gray
Write-Host ""

# 4. Show next steps
Write-Host "[4/4] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "===== Next Steps =====" -ForegroundColor Cyan
Write-Host "1. Go to Databricks Workspace -> /Users/omaressamrme@outlook.com/capstone/"
Write-Host "2. Create external locations 'data_zone' and 'checkpoint' in Unity Catalog"
Write-Host "3. Run notebook: 07-run.py to execute the entire pipeline"
Write-Host ""
