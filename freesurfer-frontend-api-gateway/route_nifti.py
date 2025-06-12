import boto3
from botocore.config import Config
from boto3.dynamodb.conditions import Key
import json
import uuid
from constants_db import NIFTIS, STATUS, TABLES, REGIONS
from constants import BUCKETS, S3_SETTINGS
from botocore.exceptions import ClientError

def putItem(item):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.NIFTIS)
    try:
        table.put_item(Item=item)
    except ClientError as e:
        return {'error': 'put_item failed' }
    return {'success': 'put_item'}

def getPresignedUrl(params):
    s3 = boto3.client('s3', config=Config(signature_version='v4'))
    upload_url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params=params,
    )
    return upload_url


def doGetLogsByNifti(nifti_uuid):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.NIFTIS)
    try:
        r = table.query(
            KeyConditionExpression=Key('nifti_uuid').eq(nifti_uuid),
            ProjectionExpression='#v1, #v2, #v3, #v4',
            ExpressionAttributeNames={
                '#v1': 'nifti_uuid',
                '#v2': 'name',
                '#v3': 'path',
                '#v4': 'logs'
            }
        )
        return r.get('Items')
    except ClientError as e:
        print("error:", e)
        return { 'error': '[doGetLogsByNifti]' }

def handlePOST(user, body):
    try:
        body_json = json.loads(body)
        if not isinstance(body_json, dict):
            return {'error': 'body JSON check failed'}
    except:
        return {'error': 'invalid body'}

    action = body_json['action']

    if action == 'get_logs':
        nifti_uuid = body_json['nifti_uuid']
        return doGetLogsByNifti(nifti_uuid)
    else:
        return {'error': 'invalid action'}



# main
def handlePathNifti(user, method, body):
    if method == "POST":
        return handlePOST(user, body)
    else:
        return {'error': f'handlePathNifti didnt find method {method}'}
