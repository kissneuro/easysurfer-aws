import json
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import pprint
import datetime as datetime
import os
from constants import BUCKETS, BATCH, TABLES, ACCESS


def getFreesurferLicenseContent():
    # a) for now just get the first table entry in users:
    db = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table_licenses = db.Table(TABLES.JOBS)
    try:
        r = table_licenses.query(
            KeyConditionExpression=Key('user').eq(user_sub),
        )
        licenses = r.get('Items')
    except ClientError as e:
        raise e

    if not len(licenses):
        print("table_licenses.query() returned empty array")
        return { 'error': 'table_licenses.query returned empty array' }



def doStartJob(user_sub, job_uuid):

    ##### STEP 0:
    getFreesurferLicenseContent(job_uuid)

    # b) write the content to s3 bucket from which the docker container can download it:
    license_content = licenses[0]['blob'] # just get the first one ....
    s3_client = boto3.client('s3')
    try:
        s3_client.put_object(
            Bucket=BUCKETS.LICENSES,
            Body=license_content,
            Key=job_uuid
        )
    except ClientError as e:
        print(e)
        return { 'error': 's3_client.put_object' }


    ###### STEP 1: get all niftis with status 's3-uploaded' associated with job_uuid
    ##             in order to calculate the job batch size
    db = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
    table = db.Table(TABLES.NIFTIS)
    print("job_uuid:", job_uuid)
    try:
        r = table.query(
            IndexName='job_uuid-index',
            KeyConditionExpression=Key('job_uuid').eq(job_uuid),
            FilterExpression='#f1 = :v1',
            ExpressionAttributeNames={
                '#f1': 'status',
            },
            ExpressionAttributeValues={
                ':v1': 's3-uploaded'
            }
        )
        niftis = r.get('Items')
    except ClientError as e:
        print(e)
        return { 'error': f'with table.query of table {TABLES.NIFTIS}' }

    num_niftis = len(niftis)
    print(f"there are {num_niftis} niftis found")
    if num_niftis == 0:
        print("num_niftis is zero, exiting...")
        return 1
    elif num_niftis == 1:
        arrayProperties = {} # if 1, it is no array job
    else:
        arrayProperties =  { 'size': num_niftis }


    ##### STEP 2: start batch
    keywords_array = dict(
        # jobName             = "{:%Y-%m-%d-%H-%M-%S-%f}".format(time_now) + "_nifti-job",
        jobName             = job_uuid,
        jobDefinition       = BATCH.JOB_DEFINITION,
        jobQueue            = BATCH.JOB_QUEUE,
        arrayProperties     = arrayProperties,
        containerOverrides  = {
            'environment': [
                { 'name' : 'JOB_ID',                'value' : job_uuid },
                { 'name' : 'MNT_ROOT',              'value' : BATCH.MNT_ROOT },
                { 'name' : 'FREESURFER_HOME',       'value' : BATCH.FREESURFER_HOME },
                { 'name' : 'SUBJECTS_DIR_ROOT',     'value' : BATCH.SUBJECTS_DIR_ROOT },
                { 'name' : 'LICENSE_S3_KEY',        'value' : job_uuid },
                { 'name' : 'NUM_CHILDREN',          'value' : str(num_niftis) },
                # on how to pass credentials to docker see: https://stackoverflow.com/a/36357388
                { 'name' : 'AWS_ACCESS_KEY_ID',     'value' : ACCESS.AWS_ACCESS_KEY_ID },
                { 'name' : 'AWS_SECRET_ACCESS_KEY', 'value' : ACCESS.AWS_SECRET_ACCESS_KEY },
            ],
        }
    )

    print("---------- STARTING JOB ----------")
    batch = boto3.client('batch', region_name=os.environ['AWS_REGION'])
    res = batch.submit_job(**keywords_array)
    # see: https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
    print("printing batch.submit_job return value using pprint.pprint:")
    pprint.pprint(res)
    print("########### Exiting ##############")
    return {
        'statusCode': 200,
    } 
