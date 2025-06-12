import boto3
import uuid
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from constants_db import REGIONS, TABLES, NIFTIS, JOBS
from constants import BUCKETS
from datetime import datetime

def doDeleteJob(job_uuid):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.NIFTIS)

    # step 1: get all niftis associated with this job
    try:
        r = table.query(
            IndexName=NIFTIS.JOB_UUID_INDEX,
            KeyConditionExpression=Key(NIFTIS.JOB_UUID_ATTR).eq(job_uuid),
            ProjectionExpression='#v1, #v2',
            ExpressionAttributeNames={
                '#v1': NIFTIS.NAME_ATTR,
                '#v2': NIFTIS.S3_KEY_ATTR,
            }
        )
        niftis = r.get('Items')
    except ClientError as e:
        print(e)
        return { 'error': 'GET handler in job' }

    # step 2: delete all found niftis in bucket:
    s3 = boto3.client('s3')
    for nifti in niftis:
        print(nifti)
        try:
            s3.delete_object(Bucket=BUCKETS.NIFTI_UPLOAD, Key=nifti[NIFTIS.S3_KEY_ATTR])
        except ClientError as e:
            print(e)
            return { "error": f"call s3 delete on nifti {nifti[NIFTIS.NAME_ATTR]} with key {nifti[NIFTIS.S3_KEY_ATTR]}"}

    # step 3: update job status to deleted:
    table = db.Table(TABLES.JOBS)
    try:
        r = table.update_item(
            Key = { JOBS.JOB_UUID_ATTR: job_uuid },
            UpdateExpression = 'SET #attr1 = :v1',
            ExpressionAttributeNames =  { "#attr1": 'status' },
            ExpressionAttributeValues = { ':v1': 'deleted' }
        )
    except ClientError as err:
        raise err

    return {
        "status": "success",
        "deleted": niftis
    }



########'# here we are ... what do we need ... ###############
### a) return a list of all niftis with status 's3-uploaded'
# (TODO: right now, files deleted by the user are marked ok.
# but no files are marked as checkout or s.th. else ... maybe we could do that in the first step of the stepper.)
### b) calculate the price ... should be simple.
# NOTE: this is just for displaying for the user. It is purely server-based.
# for now, we will do this manually... later, we could do this by stripe or s.th. else.
### dynamodb
# - we put an item checkout_num as string in dynamodb
# - and an item checkout_price as string
# - and checkout_status is 'prepared'
# ...after pressing the last button, we set it to checkout_finished <-------??
def doCheckoutJob(job_uuid, machine_uuid, fs_license_uuid):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table_niftis = db.Table(TABLES.NIFTIS)
    print("job_uuid:", job_uuid)
    print("fs_license_uuid:", fs_license_uuid)
    print("machine_uuid:", machine_uuid)

    ###### a) get all uploaded niftis associated with this job
    try:
        r = table_niftis.query(
            IndexName=NIFTIS.JOB_UUID_INDEX,
            KeyConditionExpression=Key(NIFTIS.JOB_UUID_ATTR).eq(job_uuid),
            FilterExpression='#status = :status', # das ist NICHT ConditionExpression!
            ProjectionExpression='#v1, #v2, #v3',
            ExpressionAttributeNames={
                '#status': 'status',
                '#v1': 'name',
                '#v2': 'path',
                '#v3': 'path_clean',
            },
            ExpressionAttributeValues={
                ':status': 's3-uploaded'
            }
        )
        niftis = r.get('Items')
    except ClientError as e:
        print(e)
        return { 'error': 'do checkout job' }

    # calculate price based on numbers of niftis
    print(niftis)
    price = 1
    checkout_num_STR = str(len(niftis))
    checkout_price_STR = str(checkout_num_STR * price)
    print("checkout number: ", checkout_num_STR)
    print("checkout price: ", checkout_price_STR)

    ##### step 3:
    # - update job status to checkouting:
    # - set checkout_num,
    # - set checkout_price
    # - set license uuid
    table_jobs = db.Table(TABLES.JOBS)
    try:
        r = table_jobs.update_item(
            Key = { JOBS.JOB_UUID_ATTR: job_uuid },
            UpdateExpression='SET \
            #a1 = :v1, \
            #a2 = :v2, \
            #a3 = :v3, \
            #a4 = :v4, \
            #a5 = :v5',
            ExpressionAttributeNames={
                "#a1": JOBS.STATUS_ATTR,
                "#a2": JOBS.CHECKOUT_NUM_ATTR,
                "#a3": JOBS.CHECKOUT_PRICE_ATTR,
                "#a4": JOBS.FS_LICENSE_UUID_ATTR,
                "#a5": JOBS.MACHINE_UUID_ATTR,
            },
            ExpressionAttributeValues={
                ':v1': 'checkouting',
                ':v2': checkout_num_STR,
                ':v3': checkout_price_STR,
                ':v4': fs_license_uuid,
                ':v5': machine_uuid,
            }
        )
    except ClientError as err:
        raise err


    ##### step 4: get the license and 
    return {
        "status": "success",
        "niftis": niftis,
        JOBS.CHECKOUT_NUM_ATTR: checkout_num_STR,
        JOBS.CHECKOUT_PRICE_ATTR: checkout_price_STR,
        JOBS.FS_LICENSE_UUID_ATTR: fs_license_uuid,
        JOBS.MACHINE_UUID_ATTR: machine_uuid,
    }


def doGetDownloadLink(job_uuid, path_clean):
    # TODO: check if job status is finished and if niftis job_status is SUCCCEEDED
    # see: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    # see: https://stackoverflow.com/a/61234749
    s3 = boto3.client('s3')
    # cmd = s3.get_object(
        # Bucket=BUCKETS.FINISHED,
        # Key=job_uuid + '/' + nifti_uuid + '.zip',
        # ResponseContentDisposition='attachment; filename="clean_path.zip"'
    # )
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKETS.FINISHED,
            'Key': job_uuid + '/' + path_clean + '.zip'
        }
    )
    print("got presigned urL:", url)
    return {'url': url}


def doCreateJob(user_sub, email):
    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.JOBS)
    job_uuid = str(uuid.uuid4())
    print(f"created uuid {job_uuid}")
    now_iso8601 = datetime.now().isoformat()
    print(f"creation date is epoch {now_iso8601}")

    item = {
        JOBS.JOB_UUID_ATTR: job_uuid,
        JOBS.USER_SUB_ATTR: user_sub,
        JOBS.EMAIL_ATTR: email,
        JOBS.STATUS_ATTR: 'preliminary',
        JOBS.TIME_CREATED_ATTR: now_iso8601
    }

    try:
        table.put_item(Item=item)
    except ClientError as err:
        return {'error': err }
    return {'job_uuid': job_uuid }


def handlePOST(user_sub, email, body=''):
    try:
        body_json = json.loads(body)
    except ValueError as e:
        return {'error': 'body no json'}

    action = body_json['action']
    if not action:
        return {'error': 'faulty body, action or job not found'}


    if action == 'delete':
        job_uuid = body_json['job_uuid']
        return doDeleteJob(job_uuid)
    elif action == 'checkout':
        job_uuid = body_json.get('job_uuid')
        license_uuid = body_json.get('fs_license_uuid')
        machine_uuid = body_json.get('machine_uuid')
        return doCheckoutJob(job_uuid, machine_uuid, license_uuid)
    elif action == 'create':
        return doCreateJob(user_sub, email)
    elif action == 'download':
        job_uuid = body_json['job_uuid']
        path_clean = body_json['path_clean']
        return doGetDownloadLink(job_uuid, path_clean)
    else:
        return {'error': 'faulty action keyword'}



# main
def handlePathJob(user, email, method, body='', query=''):
    if method == "POST":
        return handlePOST(user, email, body)
    else:
        return {'error': 'job handler didnt find method'}
