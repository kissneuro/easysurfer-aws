import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import constants as Consts
from constants_db import TABLES, REGIONS, NIFTIS, JOBS
from constants import BUCKETS


def doGetNiftis(job_uuid):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.NIFTIS)

    try:
        r = table.query(
            IndexName=NIFTIS.JOB_UUID_INDEX,
            KeyConditionExpression=Key(NIFTIS.JOB_UUID_ATTR).eq(job_uuid),
            ProjectionExpression='#v1, #v2, #v3, #v4, #v5, #v6',
            ExpressionAttributeNames={
                '#v1': 'nifti_uuid',
                '#v2': 'name',
                '#v3': 'status',
                '#v4': 'path',
                '#v5': 'path_clean',
                '#v6': 's3_key',
            }
        )
        return r.get('Items')
    except ClientError as e:
        raise e


def doGetLogsByJob(job_uuid):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.NIFTIS)
    try:
        r = table.query(
            IndexName=NIFTIS.JOB_UUID_INDEX,
            KeyConditionExpression=Key(NIFTIS.JOB_UUID_ATTR).eq(job_uuid),
            ProjectionExpression='#v1, #v2, #v3, #v4, #v5',
            ExpressionAttributeNames={
                '#v1': 'nifti_uuid',
                '#v2': 'name',
                '#v3': 'path',
                '#v4': 'logs',
                '#v5': 'path_clean'
            }
        )
        return r.get('Items')
    except ClientError as e:
        print("error:", e)
        return { 'error': '[doGetLogsByJob]' }


def doDeleteNiftis(nifti_uuids):
    print(f"these are the nifti_uuids: {nifti_uuids}")

    # step 1: delete all found niftis by s3 keys:
    # step 2: update job status to deleted:

    s3 = boto3.client('s3')
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.NIFTIS)

    for nifti_uuid in nifti_uuids:
        s3_key = nifti_uuid + '.nii.gz' # get the s3_key by adding .nii.gz to nifti_uuid
        try:
            s3.delete_object(Bucket=BUCKETS.NIFTI_UPLOAD, Key=s3_key)
            table.update_item(
                Key = { NIFTIS.NIFTI_UUID_ATTR: nifti_uuid },
                UpdateExpression = 'SET #attr1 = :v1',
                ExpressionAttributeNames =  { "#attr1": 'status' },
                ExpressionAttributeValues = { ':v1': 'deleted' }
            )
        except ClientError as e:
            raise e

    return {
        "status": "success",
        "deleted": json.dumps(nifti_uuids)
    }



def handlePOST(user_sub, body):
    print("handling POST")
    try:
        body_json = json.loads(body)
    except:
        return {'error': 'invalid JSON in body'}
    if not 'action' in body_json:
        return {'error': 'missing field in POST body'}

    action = body_json['action']

    if action == 'get':
        job_uuid = body_json['job_uuid']
        return doGetNiftis(job_uuid)
    elif action == 'get_logs':
        job_uuid = body_json['job_uuid']
        return doGetLogsByJob(job_uuid)
    elif action == 'delete':
        if not 'nifti_uuids' in body_json:
            return {'error': 'no field s3_keys found in body'}
        nifti_uuids = body_json.get('nifti_uuids')
        return doDeleteNiftis(nifti_uuids)
    else:
        return {'error': 'invalid action'}


# main
def handlePathNiftis(user_sub, method, body=''):
    if method == "POST":
        return handlePOST(user_sub, body)
    else:
        return {'error': f'niftis handler didnt implement method {method}'}

