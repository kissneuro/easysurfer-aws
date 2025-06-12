import boto3
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from constants_db import TABLES, REGIONS, MACHINES


def doGetMachines():
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.MACHINES)

    # TODO: here, we actually should do a scan...
    try:
        r = table.scan()
    except ClientError as e:
        print(e)
        return { 'error': 'get machines' }
    return r.get('Items')

def handlePOST(user, body):
    try:
        body_json = json.loads(body)
        action = body_json['action']
    except ValueError as e:
        print(e)
        return {'error': 'body no json'}
    
    if action == 'list':
        return doGetMachines()
    else:
        return {'error': 'action not found'}


def handlePathMachines(user, method, body=''):
    if method == "POST":
        return handlePOST(user, body)
    else:
        return {'error': 'machine handler didnt find method'}
