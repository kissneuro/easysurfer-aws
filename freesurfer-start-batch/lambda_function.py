import json
import boto3
import os
from botocore.exceptions import ClientError
from start_job import doStartJob
from constants import TABLES

###################
# INVOCATION:
#   - gets invoked by lambda function stripe-webhook on 'checkout.session.completed' event
#   - stripe-webhook is triggered by an API Gateway as triggered by stripe
#   - invocation of this function by stripe-webhook is asynchronous since stripe-webhook
#     should return ASAP.
#   - NOTE: this function has 3:00 minutes timeout!!!
#
# PARAMETER 'event':
#   is a JSON in the following format:
# {
# 'stripe_id': stripe_id,
# 'customer_id': customer_id,
# 'metadata': {
# 'user': username,
# 'user_sub': user_sub,
# 'email': email,
# 'job_uuid': job_uuis
# }
# }
# ... stripe_id and customer_id are set by stripe
# ... metadata fields are set by myself as part of the stripe-checkout
#     lambda function, which uses the auth information for user/user_sub/email
#     and the POST body by the axios user browser call to get the job_uuid
################################################





def doUpdateDb(job_uuid, stripe_id, customer_id):
    db = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table = db.Table(TABLES.JOBS)

    # update dynamodb entry to status 'paid' and add the stripe_id:
    try:
        table.update_item(
            Key = { 'job_uuid': job_uuid, }, # ist eine map, deshalb Syntax { 'key' : 'value' }
            UpdateExpression = 'SET \
                #attr1 = :v1, \
                #attr2 = :v2, \
                #attr3 = :v3, \
                #attr4 = :v4',
            ExpressionAttributeNames =  {
                "#attr1": 'status',
                "#attr2": 'stripe_id',
                "#attr3": 'customer_id',
                "#attr4": 'calculation_status',
            },
            ExpressionAttributeValues = {
                ':v1': 'paid',
                ':v2': stripe_id,
                ':v3': customer_id,
                ':v4': 'stale',
            }
        )
    except ClientError as err:
        raise err


def lambda_handler(event, context):
    metadata = event['metadata']
    user_sub = metadata['user_sub']
    job_uuid = metadata['job_uuid']
    stripe_id = event['stripe_id']
    customer_id = event['customer_id']
    print(f"resolved fields in event:\
        user_sub: {user_sub},\
        job_uuid: {job_uuid},\
        stripe_id: {stripe_id},\
        customer_id: {customer_id}")

    doUpdateDb(job_uuid, stripe_id, customer_id)


    # start the job:
    doStartJob(user_sub, job_uuid)


    print("########### Exiting ##############")
    return {
        'statusCode': 200,
    }
