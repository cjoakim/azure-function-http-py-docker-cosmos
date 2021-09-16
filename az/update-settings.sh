#!/bin/bash

# Bash and az CLI script to update Function App Settings
# Chris Joakim, Microsoft, September 2021

name="cjoakimfunctions"
region="eastus"

echo 'setting appsettings ...'

# az functionapp config appsettings set \
#     --name $name \
#     --resource-group $name \
#     --settings AzureWebJobsStorage=$conn_str

# az functionapp config appsettings set \
#     --name $name \
#     --resource-group $name \
#     --settings AzureWebJobsStorage=$AZURE_COSMOSDB_SQLDB_URI

# az functionapp config appsettings set \
#     --name $name \
#     --resource-group $name \
#     --settings AZURE_COSMOSDB_SQLDB_URI=$AZURE_COSMOSDB_SQLDB_URI

# az functionapp config appsettings set \
#     --name $name \
#     --resource-group $name \
#     --settings AZURE_COSMOSDB_SQLDB_KEY=$AZURE_COSMOSDB_SQLDB_KEY

# az functionapp config appsettings set \
#     --name $name \
#     --resource-group $name \
#     --settings AZURE_FUNCTION_SECRET1=$AZURE_FUNCTION_SECRET1

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AZURE_FUNCTION_MAX_QUERIES=100

sleep 30

echo 'appsettings list ...'
az functionapp config appsettings list \
    --name $name \
    --resource-group $name

echo 'done'
