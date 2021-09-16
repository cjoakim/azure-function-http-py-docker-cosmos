#!/bin/bash

# Build the Docker container for this Azure Function app.
# Chris Joakim, Microsoft, September 2021

name="cjoakim/azure-function-http-py-cosmos"

docker build -t $name .

docker image ls | grep $name

# Notes:
# docker build -t cjoakim/azure-function-http-py-cosmos . 
# docker image ls
# docker ps
# docker stop -t 2 008038664a58
#
# DockerHub:
# docker push cjoakim/azure-function-http-py-cosmos:latest
#
# Azure Container Registry:
# az acr login --name cjoakimacr
# az acr repository list --name cjoakimacr --output table
# docker tag cjoakim/azure-function-http-py-cosmos:latest cjoakimacr.azurecr.io/azure-function-http-py-cosmos:latest
# docker push cjoakimacr.azurecr.io/azure-function-http-py-cosmos:latest
