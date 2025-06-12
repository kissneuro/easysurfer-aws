import boto3
from botocore.exceptions import ClientError
import json
from constants import COGNITO

def deleteAccount(user_sub):
    client_idp = boto3.client('cognito-idp')
    try:
        res = client_idp.admin_delete_user(
            UserPoolId=COGNITO.COGNITO_POOL_ID,
            Username=user_sub
        )
    except ClientError as e:
        raise e

    print("[deleteAccount] admin_delete_user(): ", res)
    return {'success': 'deleteAccount',
        'res': json.dumps(res)}

def handlePOST(user_sub, body):
    body_json = json.loads(body)
    action = body_json.get('action')

    if action == 'delete':
        return deleteAccount(user_sub)
    else:
        return {'error': 'action not implemented'}

def handlePathAccount(user_sub, method, body=''):
    if method == 'POST':
        return handlePOST(user_sub, body)
    else:
        return {'error': 'method not implemented'}
