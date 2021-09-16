import json
import logging
import os
import time
import traceback

from datetime import datetime

# import arrow

import azure.functions as func

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import azure.cosmos.diagnostics as diagnostics
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as partition_key

REQUEST_CHARGE_HEADER = 'x-ms-request-charge'
DURATION_MS_HEADER    = 'x-ms-request-duration-ms'
ITEM_COUNT_HEADER     = 'x-ms-item-count'
HEADERS_OF_INTEREST   = [
    REQUEST_CHARGE_HEADER, DURATION_MS_HEADER, ITEM_COUNT_HEADER]

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    database, container = None, None
    client, db_proxy, ctr_proxy = None, None, None
    record_diagnostics = diagnostics.RecordDiagnostics()
    cosmos_error, other_error = None, None

    try:
        fname = context.function_name
        inv_id = context.invocation_id
        logging.info(f'{fname}, invocation_id: {inv_id}')
        
        expected_token = os.environ['AZURE_FUNCTION_SECRET1']
        provided_token = req.headers['Auth-Token']
        #logging.info('provided_token: {provided_token}'.format(provided_token))

        if expected_token == provided_token:
            post_data = req.get_json()  # get_json() returns an object (i.e. - dict)
            dbname  = post_data['database']
            cname   = post_data['container']
            queries = post_data['queries']

            response_obj = dict()
            response_obj['_function_name'] = fname
            response_obj['_invocation_id'] = inv_id
            response_obj['post_data'] = post_data
            response_obj['results'] = list()
            logging.info(response_obj)

            if len(queries) > 0:
                connect_start_epoch = datetime.now().timestamp()
                client    = get_cosmos_client()
                db_proxy  = get_db_proxy(client, dbname)
                ctr_proxy = get_ctr_proxy(db_proxy, cname)
                connect_finish_epoch = datetime.now().timestamp()
                response_obj['cosmos_client_connect_seconds'] = connect_finish_epoch - connect_start_epoch

                query_count = 0
                max_query_count = get_max_query_count()
                logging.info('max_query_count: {}'.format(max_query_count))

                for query in queries:
                    logging.info(query)
                    sql = query['sql']
                    client_verbose = str(query['verbose']).lower() == 'true'
                       
                    count = int(query['count'])
                    for idx in range(count):
                        query_count = query_count + 1
                        if query_count <= max_query_count:
                            result = dict()
                            result['seq'] = query_count
                            result['idx'] = idx
                            result['sql'] = sql
                            query_container(ctr_proxy, result, sql, client_verbose)
                            response_obj['results'].append(result)             

                jstr = json.dumps(response_obj, indent=2, sort_keys=True)
                return func.HttpResponse(jstr)
            else:
                return func.HttpResponse("Bad Request", status_code=400) 
        else:
            # HTTP/1.1 401 Unauthorized
            return func.HttpResponse("Unauthorized", status_code=401)
    except:
        return func.HttpResponse("Error", status_code=500)

def get_max_query_count():
    try:
        s = os.environ['AZURE_FUNCTION_MAX_QUERIES']
        logging.info('get_max_query_count; s: {}'.formats(s))
        if s == None:
            return 20
        return int(s)
    except:
        return 20

def get_cosmos_client():
    uri = os.environ['AZURE_COSMOSDB_SQLDB_URI']
    key = os.environ['AZURE_COSMOSDB_SQLDB_KEY']
    logging.info('uri: {} key: {}'.format(uri, key))
    return cosmos_client.CosmosClient(uri, {'masterKey': key})

def get_db_proxy(c, name):
    logging.info('get_db_proxy: {} {}'.format(c, name))
    return c.get_database_client(database=name)

def get_ctr_proxy(db_proxy, name):
    logging.info('get_ctr_proxy: {} {}'.format(db_proxy, name))
    return db_proxy.get_container_client(name)

def query_container(cproxy, result, sql, client_verbose):  
    try:
        rd = diagnostics.RecordDiagnostics()
        logging.info('query_container, sql: {}'.format(sql))
        if client_verbose:
            result['docs'] = list()

        epoch1 = datetime.now().timestamp()

        docs = cproxy.query_items(
            query=sql,
            enable_cross_partition_query=True,
            max_item_count=100,
            populate_query_metrics=True,
            response_hook=rd)

        for doc in docs:
            if client_verbose:
                result['docs'].append(doc)

        epoch2 = datetime.now().timestamp()
        result['client_query_ms'] = (epoch2 - epoch1) * 1000.0

        for header_name in HEADERS_OF_INTEREST:
            if header_name in rd.headers:
                result[header_name] = rd.headers[header_name]
            else:
                result[header_name] = -1

    except CosmosHttpResponseError as ce:
        result['cosmos_error'] = str(ce)
        logging.error(ce)
    except Error as e:
        result['other_error'] = str(e)
        logging.error(e)
    except:
        result['other_error'] = '?' 


# https://github.com/Azure/azure-sdk-for-python/blob/azure-cosmos_4.2.0/sdk/cosmos/azure-cosmos/azure/cosmos/exceptions.py
