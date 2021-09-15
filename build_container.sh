#!/bin/bash

# Build the Docker container for this Azure Function app.
# Chris Joakim, Microsoft, September 2021

name="cjoakim/az-function-http-py-cosmos"

docker build -t $name .

docker image ls | grep $name
