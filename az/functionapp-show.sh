#!/bin/bash

name="cjoakimfunctions"
region="eastus"

echo 'listing function apps ...'
az functionapp list \
    --resource-group  $name

echo 'showing function app ...'
az functionapp show \
    --name $name \
    --resource-group  $name

echo 'appsettings list ...'
az functionapp config appsettings list \
    --name $name \
    --resource-group $name

echo 'listing functions with func command ...'
func azure functionapp list-functions $name
