# azure-function-http-py-docker-cosmos

A Containerized Python HTTP-triggered Azure Function which queries CosmosDB

## Links

- https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local

- https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python


## Workstation Requirements

See the above links, the following are required to be installed:

- Azure Functions Core Tools, version 3.x
- Azure CLI, version 2.4 or later.
- Python 3.8 (64-bit)
- Docker


## Function Creation

### Verify the Azure Functions Core Tools version

```
$ func --version
3.0.3734           <-- OK, version 3
```

```
$ func init --worker-runtime python --docker
```