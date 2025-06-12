import json
from route_key_post import handleRouteKeyPOST
from route_jobs import handlePathJobs
from route_job import handlePathJob
from route_niftis import handlePathNiftis
from route_machines import handlePathMachines
from route_license import handlePathLicense
from route_nifti import handlePathNifti
from route_mail import handlePathMail
from route_account import handlePathAccount
from pathlib import Path


def handleRouteKeyANY(route_key):
    return {'recognized_match': "ANY /"}

def handleRouteKeyGET(route_key):
    return {'recognized_match': "GET /"}

def lambda_handler(event, context):
    print(event)

    # these are the parameters when using API Gateway HTTP implementation:
    # route_key = event['routeKey']
    # raw_path = event['rawPath']
    # method = event['requestContext']['http']['method']
    # jwt_claims = event['requestContext']['authorizer']['jwt']['claims']

    # debugging
    # return {
    # 'statusCode': 200,
    # 'body': json.dumps(event)
    # }

    # these are the parameters when using API Gateway REST implementation:
    route_resource   = event['resource'] # not always matching path, e.g. "/{proxy+}"
    raw_path         = event['path']
    http_method      = event['httpMethod']
    jwt_claims       = event['requestContext']['authorizer']['claims']
    user_sub         = jwt_claims['sub']
    cognito_username = jwt_claims['cognito:username']
    email            = jwt_claims['email']
    # fields are not always present - check before assigning

    query = {} # the query is valid json
    body = '' # the body is not, which is why - when set - has to be passed to json.loads()
    if 'body' in event:
        body = event['body']
    if 'queryStringParameters' in event:
        query = event['queryStringParameters']


    # url_splits = raw_path.split('/', -1)
    # route_root = url_splits[1] # [0] is plain '/'
    # route_tails = url_splits[2:]   

    if raw_path == '/jobs':
        r = handlePathJobs(user_sub, http_method, body=body)
    elif raw_path == '/job':
        r = handlePathJob(user_sub, email, http_method, body=body)
    elif raw_path == '/mail':
        r = handlePathMail(user_sub, http_method, email, body=body)
    elif raw_path == '/nifti':
        r = handlePathNifti(user_sub, http_method, body=body)
    elif raw_path == '/niftis':
        r = handlePathNiftis(user_sub, http_method, body=body)
    elif raw_path == '/machines':
        r = handlePathMachines(user_sub, http_method, body=body)
    elif raw_path == '/license':
        r = handlePathLicense(user_sub, http_method, body=body)
    elif raw_path == '/account':
        r = handlePathAccount(user_sub, http_method, body=body)
    else:
        r = event

    print(r)
    return {
        'headers': {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT"
        },
        'statusCode': 200,
        'body': json.dumps(r) # IMPORTANT
    }

# CORS headers are already configured in API Gateway console
# 'headers': {
# "Access-Control-Allow-Headers" : "Content-Type",
# "Access-Control-Allow-Origin": "*",
# 'Access-Control-Allow-Credentials': True,
# "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
# },
