# azure-function-http-py-docker-cosmos

A Containerized Python HTTP-triggered Azure Function which queries CosmosDB.

Useful for performance testing.

## Links

- https://docs.microsoft.com/en-us/azure/azure-functions/

- https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local

- https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image?tabs=in-process%2Cbash%2Cazure-cli&pivots=programming-language-python

- https://docs.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python

---

## Workstation Requirements

See the above links, the following are required to be installed:

- Azure Functions Core Tools, version 3.x
- Azure CLI, version 2.4 or later.
- Python 3.8 (64-bit)
- Docker

---

## Function Creation on Developer Workstation

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
azure-cosmos
azure-functions
```

I use **pyenv** to create python virtual environments, see pyenv.sh. 
Use your preferred tool/library for this.

```
$ ./pyenv.sh
...
=== pip list ...
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

### Implement the Function 

Edit the generated [HttpCosmos/__init__.py](HttpCosmos/__init__.py) script which implements the Azure Function.

---

## Environment Variables 

This Azure Function expects the following **environment variables**:

- AZURE_COSMOSDB_SQLDB_URI
- AZURE_COSMOSDB_SQLDB_KEY
- AZURE_FUNCTION_SECRET1
- AZURE_FUNCTION_MAX_QUERIES

The Function uses the first two to connect to your CosmosDB Account.
You can get these values in Azure Portal.

AZURE_FUNCTION_SECRET1 is used to authenticate each HTTP request
to prevent anonymous access.  This same value must be passed
from the HTTP client as the **Auth-Token** HTTP header value.
See [curl_client.sh](curl_client.sh).

AZURE_FUNCTION_MAX_QUERIES is used to specify a maximum number of 
Cosmos SQL queries that can be executed for each invocation of the
Function.

---

## The JSON Body POSTed to this Azure Function

The following is an example; see [postdata/body1.json](postdata/body1.json)

The POSTed JSON body must contain **database**, **container**, and
**queries** attributes as shown below.

Each of the elements in the **queries** array must be an object which 
contains the **sql**, (iteration) **count**, and **verbose** arguments.

The **count** is the number of times the sql query will be executed
within the Function invocation.

The **verbose** flag, if "true", will return the documents returned by the
sql query, in the HTTP response from the Function.

```
{
  "database": "dev",
  "container": "travel",
  "queries": [
    {
      "sql": "select * from c where c.pk = 'BOS:KEF' and c.id = '65629b25-f738-44c7-9406-985c50bbbcd4'",
      "count": 1,
      "verbose": "true"
    },
    {
      "sql": "select * from c where c.pk = 'GUM:MAJ' offset 0 limit 1",
      "count": 1,
      "verbose": "false"
    },
    {
      "sql": "select * from c where c.pk = 'CLT:MBJ' offset 0 limit 1",
      "count": 3,
      "verbose": "false"
    }
  ]
}
```

See **postdata.py** which can be used to generate this JSON file.

--- 

## Develop and Test the Function Locally

In one shell (bash or PowerShell) window, start the function app:

```
$ func start
```

In another shell execute the HTTP client script:

```
$ ./curl_client.sh local_func
```

---

## Build and Test the Docker Container Locally

### Build the Container

Modify this script to change **cjoakim** to your name.

```
$ ./build_container.sh
```

### DockerHub

The containerized application is available as a public image on DockerHub:

```
cjoakim/azure-function-http-py-cosmos:latest
```

### Start the Container with Docker Compose

```
$ ./compose.sh up
```

### Execute the HTTP Client

In another shell execute the HTTP client script:

```
$ ./curl_client.sh local_docker
```

### Stop the Container with Docker Compose

```
$ ./compose.sh down
```

---

## Invoke the Function App on Azure

```
$ ./curl_client.sh azure

using url: https://cjoakimfunctions.azurewebsites.net/api/HttpCosmos

{
  "_datetime": "2021-09-16 17:11:13.988846",
  "_function_name": "HttpCosmos",
  "_invocation_id": "2463fb52-13f8-4df3-a9e0-9e88675c88c2",
  "cosmos_client_connect_seconds": 0.17673707008361816,
  "post_data": {
    "container": "travel",
    "database": "dev",
    "queries": [
      {
        "count": 1,
        "sql": "select * from c where c.pk = 'BOS:KEF' and c.id = '65629b25-f738-44c7-9406-985c50bbbcd4'",
        "verbose": "true"
      },
      {
        "count": 1,
        "sql": "select * from c where c.pk = 'GUM:MAJ' offset 0 limit 1",
        "verbose": "false"
      },
      {
        "count": 3,
        "sql": "select * from c where c.pk = 'CLT:MBJ' offset 0 limit 1",
        "verbose": "false"
      }
    ]
  },
  "results": [
    {
      "client_query_ms": 196.7029571533203,
      "docs": [
        {
          "_attachments": "attachments/",
          "_etag": "\"1000e5bc-0000-0100-0000-613b6a970000\"",
          "_rid": "pVIbAKevu-sDAAAAAAAAAA==",
          "_self": "dbs/pVIbAA==/colls/pVIbAKevu-s=/docs/pVIbAKevu-sDAAAAAAAAAA==/",
          "_ts": 1631283863,
          "airlineid": "20402",
          "carrier": "GL",
          "count": "1",
          "date": "2007/03/01",
          "doc_epoch": 1631283859866,
          "doc_time": "2021/09/10-14:24:19",
          "from_airport_name": "General Edward Lawrence Logan Intl",
          "from_airport_tz": "America/New_York",
          "from_iata": "BOS",
          "from_location": {
            "coordinates": [
              -71.005181,
              42.364347
            ],
            "type": "Point"
          },
          "id": "65629b25-f738-44c7-9406-985c50bbbcd4",
          "month": "3",
          "pk": "BOS:KEF",
          "route": "BOS:KEF",
          "to_airport_country": "Iceland",
          "to_airport_name": "Keflavik International Airport",
          "to_airport_tz": "Atlantic/Reykjavik",
          "to_iata": "KEF",
          "to_location": {
            "coordinates": [
              -22.605556,
              63.985
            ],
            "type": "Point"
          },
          "year": "2007"
        }
      ],
      "idx": 0,
      "seq": 1,
      "sql": "select * from c where c.pk = 'BOS:KEF' and c.id = '65629b25-f738-44c7-9406-985c50bbbcd4'",
      "x-ms-item-count": "1",
      "x-ms-request-charge": "2.93",
      "x-ms-request-duration-ms": "0.982"
    },
    {
      "client_query_ms": 33.29801559448242,
      "idx": 0,
      "seq": 2,
      "sql": "select * from c where c.pk = 'GUM:MAJ' offset 0 limit 1",
      "x-ms-item-count": "1",
      "x-ms-request-charge": "2.83",
      "x-ms-request-duration-ms": "0.737"
    },
    {
      "client_query_ms": 101.33194923400879,
      "idx": 0,
      "seq": 3,
      "sql": "select * from c where c.pk = 'CLT:MBJ' offset 0 limit 1",
      "x-ms-item-count": "0",
      "x-ms-request-charge": "2.79",
      "x-ms-request-duration-ms": "0.609"
    },
    {
      "client_query_ms": 56.95390701293945,
      "idx": 1,
      "seq": 4,
      "sql": "select * from c where c.pk = 'CLT:MBJ' offset 0 limit 1",
      "x-ms-item-count": "0",
      "x-ms-request-charge": "2.79",
      "x-ms-request-duration-ms": "0.882"
    },
    {
      "client_query_ms": 114.48121070861816,
      "idx": 2,
      "seq": 5,
      "sql": "select * from c where c.pk = 'CLT:MBJ' offset 0 limit 1",
      "x-ms-item-count": "0",
      "x-ms-request-charge": "2.79",
      "x-ms-request-duration-ms": "0.645"
    }
  ]
}
```