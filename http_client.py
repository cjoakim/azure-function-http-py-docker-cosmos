"""
Usage:
  python http_client.py <function_url> <auth_secret> <body_json_file>

  python http_client.py https://cjoakimfunctions.azurewebsites.net/api/HttpCosmos ppqXXXXX postdata/body1.json
"""

import json
import sys
import requests

def read_body_json_file(body_json_file):
    with open(body_json_file, 'rt') as f:
        return f.read()

if __name__ == "__main__":
    function_url   = sys.argv[1]
    auth_secret    = sys.argv[2]
    body_json_file = sys.argv[3]

    body = json.loads(read_body_json_file(body_json_file))

    print('function_url:   {}'.format(function_url))
    print('auth_secret:    {}'.format(auth_secret))
    print('body_json_file: {}'.format(body_json_file))
    print('body:')
    print(json.dumps(body, sort_keys=False, indent=2))

    headers = dict()
    headers['Content-Type'] = 'application/json'
    headers['Auth-Token'] = auth_secret
    print('headers:')
    print(json.dumps(headers, sort_keys=False, indent=2))
    print('---')
    print('response:')

    response = requests.post(
        function_url, headers=headers, json=body)

    print('response: {}'.format(response))

    if response.status_code == 200:
        resp_obj = json.loads(response.text)
        print(json.dumps(resp_obj, sort_keys=False, indent=2))
