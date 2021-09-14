#!/bin/bash

curl -v -X POST \
    -H "Content-Type: application/json" \
    -H "Auth-Token:"$AZURE_FUNCTION_SECRET1 \
    -d '{"sql":"select * from c where c.pk = 'ANC:OKO' offset 0 limit 1", "count":"3", "sleep_ms":"10.0"}' \
    "http://localhost:7071/api/HttpCosmos"

