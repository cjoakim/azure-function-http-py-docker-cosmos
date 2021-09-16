#!/bin/bash

# HTTP client script for this Azure Function - using bash shell and curl.
# Chris Joakim, Microsoft, September 2021
#
# Usage:
# $ ./curl_client.sh local_func    <-- invoke the Function started by 'func start'
# $ ./curl_client.sh local_docker  <-- invoke the locally running Docker container
# $ ./curl_client.sh azure         <-- invoke the deployed Function in Azure

local_func_url="http://localhost:7071/api/HttpCosmos"
local_docker_url="http://localhost:8080/api/HttpCosmos"
azure_function_url="https://cjoakimfunctions.azurewebsites.net/api/HttpCosmos"

if [ "$1" == 'local_func' ]
then 
    url=$local_func_url
fi

if [ "$1" == 'local_docker' ]
then 
    url=$local_docker_url
fi

if [ "$1" == 'azure' ]
then 
    url=$azure_function_url
fi

echo 'using url: '$url

curl -X POST \
    -H "Content-Type: application/json" \
    -H "Auth-Token:"$AZURE_FUNCTION_SECRET1 \
    -d @postdata/body1.json \
    $url
