# azure-function-http-py-docker-cosmos

A Containerized Python HTTP-triggered Azure Function which queries CosmosDB

## Links

- https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local

- https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python

- https://docs.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python


## Workstation Requirements

See the above links, the following are required to be installed:

- Azure Functions Core Tools, version 3.x
- Azure CLI, version 2.4 or later.
- Python 3.8 (64-bit)
- Docker


---

## Function Creation

### Verify the Azure Functions Core Tools version

```
$ func --version
3.0.3734           <-- OK, version 3
```

### Create the Function App

```
$ func init --worker-runtime python --docker
```

### Create a HTTP Function in the App

```
$ func new --name HttpCosmos --template "HTTP trigger" --authlevel anonymous
```

### Start the Function

```
$ func start
Found Python version 3.8.6 (python3).

Azure Functions Core Tools
Core Tools Version:       3.0.3734 Commit hash: 61192bb28820be76916f85209916152801483456  (64-bit)
Function Runtime Version: 3.1.4.0
...
Functions:
	HttpCosmos: [GET,POST] http://localhost:7071/api/HttpCosmos
...
```

### Invoke the Function

I'll use [curl](https://curl.se/) in this repo, but you can use your preferred HTTP Client software.

```
$ curl -v http://localhost:7071/api/HttpCosmos
...
< HTTP/1.1 200 OK
...
```

Control-C to stop the Function App

### Implementing the Function 

Create a python virtual environment for the App, with these Python libraries
in file **requirements.txt**.

```
arrow
azure-cosmos
azure-functions
```

I use **pyenv** to create python virtual environments, see pyenv.sh. 
Use your preferred tool/library for this.

```
$ ./pyenv.sh
...
$ pip list
Package            Version
------------------ ---------
arrow              1.1.1
azure-core         1.18.0
azure-cosmos       4.2.0
azure-functions    1.7.2
certifi            2021.5.30
charset-normalizer 2.0.5
click              8.0.1
idna               3.2
pep517             0.11.0
pip                21.2.4
pip-tools          6.2.0
pyspark            3.1.2
python-dateutil    2.8.2
requests           2.26.0
setuptools         49.2.1
six                1.16.0
tomli              1.2.1
urllib3            1.26.6
wheel              0.37.0
```
