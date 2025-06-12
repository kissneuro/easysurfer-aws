import boto3
import json
import uuid
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from constants_db import REGIONS, TABLES, LICENSES

def getLicenses(user):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table_licenses = db.Table(TABLES.LICENSES)

    try:
        r = table_licenses.query(
            IndexName=LICENSES.USER_SUB_INDEX,
            KeyConditionExpression=Key(LICENSES.USER_SUB_ATTR).eq(user)
        )
        return r.get('Items')
    except ClientError as e:
        raise e

def putLicense(user, licenses):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table_licenses = db.Table(TABLES.LICENSES)

    label = licenses.get('label')
    blob = licenses.get('blob')
    uuid_license = str(uuid.uuid4())

    item = {
        LICENSES.UUID_ATTR: uuid_license,
        LICENSES.USER_SUB_ATTR: user,
        LICENSES.LABEL_ATTR: label,
        LICENSES.BLOB_ATTR: blob
    }

    try:
        table_licenses.put_item(Item=item)
        return {'uuid': uuid_license}
    except ClientError as err:
        return { 'error': err }

def deleteLicense(license_uuid):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table_licenses = db.Table(TABLES.LICENSES)

    try:
        table_licenses.delete_item(
            Key = { LICENSES.UUID_ATTR: license_uuid }
        )
    except ClientError as e:
        raise e

    return {'success': f'license entry with uuid {license_uuid} deleted'}


def handlePOST(user, body):
    try:
        body_json = json.loads(body)
    except Exception as e:
        print("error in handlePost --> json.loads: ", e)
        return {'error': 'faulty payload'}

    action = body_json.get('action')
    if action == 'get':
        return getLicenses(user)
    elif action == 'put':
        return putLicense(user, body_json.get('license'))
    elif action == 'delete':
        uuid_license = body_json.get('uuid')
        return deleteLicense(uuid_license)
    else:
        return {'error': 'invalid action'}


def handlePathLicense(user, method, body=''):
    if method == 'POST':
        return handlePOST(user, body)
    else:
        return {'error': 'job handler didnt find method'}
