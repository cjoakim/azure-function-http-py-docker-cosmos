import json
import logging
import os
import time

from datetime import datetime

# import arrow

import azure.functions as func

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import azure.cosmos.documents as documents


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    client = None
    try:
        fname = context.function_name
        inv_id = context.invocation_id
        logging.info(f'{fname}, invocation_id: {inv_id}')
        
        expected_token = os.environ['AZURE_FUNCTION_SECRET1']
        provided_token = req.headers['Auth-Token']
        logging.info(f'provided_token: {provided_token}')

        if expected_token == provided_token:
            post_data = req.get_json()  # get_json() returns an object (i.e.- dict), not a str
            sql = post_data['sql']
            count = int(post_data['count'])
            sleep_ms = get_sleep_ms(post_data)
            valid_request = False

            response_obj = dict()
            response_obj['function_name'] = fname
            response_obj['invocation_id'] = inv_id
            response_obj['sql']   = sql
            response_obj['count'] = count
            response_obj['sleep_ms'] = sleep_ms
            response_obj['results'] = list()
            logging.info(response_obj)

            if request_is_valid(sql, count):
                client = get_cosmos_client()
                logging.info('client {}'.format(client))

                for i in range(count):
                    #time.sleep(sleep_ms)
                    result = dict()
                    result['i'] = i
                    #result['epoch'] = datetime.now().timestamp()
                    response_obj['results'].append(result)

                jstr = json.dumps(response_obj, indent=2, sort_keys=False)
                logging.info(jstr)
                return func.HttpResponse(jstr)
            else:
                return func.HttpResponse("Bad Request", status_code=400) 
        else:
            # HTTP/1.1 401 Unauthorized
            return func.HttpResponse("Unauthorized", status_code=401)
    except:
        return func.HttpResponse("Error", status_code=500)

def get_sleep_ms(post_data):
    try:
        return float(post_data['sleep_ms'])
    except:
        return 0.1

def request_is_valid(sql, count):
    if (count > 0) and (count <= 100):
        if sql.lower().startswith('select '):
            return True
    return False

def get_cosmos_client():
    uri = os.environ['AZURE_COSMOSDB_SQLDB_URI']
    key = os.environ['AZURE_COSMOSDB_SQLDB_KEY']
    logging.info('uri: {} key: {}'.format(uri, key))
    return cosmos_client.CosmosClient(uri, {'masterKey': key})

