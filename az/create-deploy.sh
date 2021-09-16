#!/bin/bash

# Bash and az CLI script to create the necessary Azure PaaS Services
# (Storage, Function App Plan, Function App) and deploy the Docker Container
# to this Function App.
# Chris Joakim, Microsoft, September 2021


# See https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python

name="cjoakimfunctions"
region="eastus"
docker_image="cjoakim/azure-function-http-py-cosmos:latest"

echo 'creating resource group ...'
az group create \
    --name $name \
    --location $region

sleep 30

echo 'creating storage account ...'
az storage account create \
    --name $name \
    --location $region \
    --resource-group $name \
    --sku Standard_LRS

sleep 30

echo 'getting storage connection string ...'
az storage account show-connection-string \
    --resource-group  $name \
    --name $name \
    --query connectionString \
    --output tsv > tmp/storage.txt

conn_str=`cat tmp/storage.txt | head -1`
echo $conn_str

sleep 30 

echo 'creating function app plan ...'
az functionapp plan create \
    --resource-group $name \
    --name $name \
    --location $region \
    --number-of-workers 1 \
    --sku EP1 \
    --is-linux

sleep 30

echo 'creating function app ...'
az functionapp create \
    --name $name \
    --storage-account $name \
    --resource-group  $name \
    --plan            $name \
    --functions-version 3 \
    --deployment-container-image-name $docker_image

sleep 30

echo 'setting appsettings ...'

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AzureWebJobsStorage=$conn_str

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AzureWebJobsStorage=$AZURE_COSMOSDB_SQLDB_URI

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AZURE_COSMOSDB_SQLDB_URI=$AZURE_COSMOSDB_SQLDB_URI

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AZURE_COSMOSDB_SQLDB_KEY=$AZURE_COSMOSDB_SQLDB_KEY

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AZURE_FUNCTION_SECRET1=$AZURE_FUNCTION_SECRET1

az functionapp config appsettings set \
    --name $name \
    --resource-group $name \
    --settings AZURE_FUNCTION_MAX_QUERIES=60

sleep 30

echo 'appsettings list ...'
az functionapp config appsettings list \
    --name $name \
    --resource-group $name

echo 'done'
