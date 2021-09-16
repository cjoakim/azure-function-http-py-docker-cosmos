import json
import logging
import os
import time
import traceback

from datetime import datetime

# import arrow

import azure.functions as func

# import azure.cosmos.cosmos_client as cosmos_client
# import azure.cosmos.errors as errors
# import azure.cosmos.http_constants as http_constants
# import azure.cosmos.documents as documents

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import azure.cosmos.diagnostics as diagnostics
import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as partition_key

REQUEST_CHARGE_HEADER = 'x-ms-request-charge'
DURATION_MS_HEADER    = 'x-ms-request-duration-ms'


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    database, container = None, None
    client, database_proxy, container_proxy = None, None, None
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
            response_obj['function_name'] = fname
            response_obj['invocation_id'] = inv_id
            response_obj['post_data'] = post_data
            response_obj['results'] = list()
            logging.info(response_obj)

            if len(queries) > 0:
                connect_start_epoch = datetime.now().timestamp()
                client          = get_cosmos_client()
                database_proxy  = get_database_proxy(client, dbname)
                container_proxy = get_container_proxy(database_proxy, cname)
                connect_finish_epoch = datetime.now().timestamp()
                response_obj['connect_seconds'] = connect_finish_epoch - connect_start_epoch

                query_count = 0
                max_query_count = get_max_query_count()
                logging.info('max_query_count: {}'.format(max_query_count))

                for query in queries:
                    logging.info(query)
                    sql = query['sql']
                    client_verbose = str(query['verbose']).lower() == 'true'
                    count = int(query['count'])
                    for i in range(count):
                        query_count = query_count + 1
                        if query_count <= max_query_count:
                            result = dict()
                            result['seq'] = query_count
                            result['i'] = i
                            result['sql'] = sql
                            result['docs'] = list()
                            epoch1 = datetime.now().timestamp()
                            doc_count = 0

                            record_diagnostics = diagnostics.RecordDiagnostics()
                            cosmos_error, other_error = None, None
                            query_results = query_container(
                                container_proxy, sql, True, 100, record_diagnostics)

                            logging.error(record_diagnostics)
                            
                            if query_results == None:
                                if cosmos_error != None:
                                    logging.info(cosmos_error)
                                    result['cosmos_error'] = str(cosmos_error)
                                if other_error != None:
                                    logging.info(other_error)
                                    result['cosmos_error'] = str(cosmos_error)
                            else:
                                for doc in query_results:
                                    doc_count = doc_count + 1
                                    logging.info('doc id: {}'.format(doc['id']))
                                    if client_verbose:
                                        result['docs'].append(doc)
                            epoch2 = datetime.now().timestamp()

                            headers = record_diagnostics.headers
                            for key in sorted(headers.keys()):
                                logging.info('header: {} -> {}'.format(key, headers[key]))
                            if REQUEST_CHARGE_HEADER in headers:
                                result['ru'] = record_diagnostics.headers[REQUEST_CHARGE_HEADER]
                            else:
                                result['ru'] = -1
                            if DURATION_MS_HEADER in headers:
                                result['cosmos_query_ms'] = float(record_diagnostics.headers[DURATION_MS_HEADER])
                            else:
                                result['cosmos_query_ms'] = -1
                            result['doc_count'] = doc_count
                            result['client_query_ms'] = (epoch2 - epoch1) * 1000.0
                            response_obj['results'].append(result)

                jstr = json.dumps(response_obj, indent=2, sort_keys=False)
                #logging.info(jstr)
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

def get_database_proxy(c, name):
    logging.info('get_database_proxy: {} {}'.format(c, name))
    return c.get_database_client(database=name)

def get_container_proxy(db_proxy, name):
    logging.info('get_container_proxy: {} {}'.format(db_proxy, name))
    return db_proxy.get_container_client(name)

def query_container(ctrproxy, sql, xpartition, max_items, rd):
    try:
        logging.info('query_container, sql: {} {} {}'.format(
            sql, xpartition, max_items))
        return ctrproxy.query_items(
            query=sql,
            enable_cross_partition_query=xpartition,
            max_item_count=max_items,
            populate_query_metrics=True,
            response_hook=rd)
    except CosmosHttpResponseError as ce:
        cosmos_error = ce
        logging.error(ce)
        return None
    except Error as err:
        other_error = err
        logging.error(err) 
        return None

# https://github.com/Azure/azure-sdk-for-python/blob/azure-cosmos_4.2.0/sdk/cosmos/azure-cosmos/azure/cosmos/exceptions.py
