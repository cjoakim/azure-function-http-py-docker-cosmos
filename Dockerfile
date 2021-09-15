# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8-appservice

FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot

# docker build -t cjoakim/az-function-http-py-cosmos . 
# docker image ls
# docker ps
# docker stop -t 2 008038664a58
#
# DockerHub:
# docker push cjoakim/az-function-http-py-cosmos:latest
#
# Azure Container Registry:
# az acr login --name cjoakimacr
# az acr repository list --name cjoakimacr --output table
# docker tag cjoakim/az-function-http-py-cosmos:latest cjoakimacr.azurecr.io/az-function-http-py-cosmos:latest
# docker push cjoakimacr.azurecr.io/az-function-http-py-cosmos:latest

