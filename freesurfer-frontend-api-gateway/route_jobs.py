import boto3
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from constants_db import REGIONS, TABLES, JOBS
from operator  import or_
from functools import reduce

#
#
# Projection Expressions: which columns should be retrieved in GetItem, Query or Scan
#   by default, these are all columns. Legacy parameter: AttributesToGet
#   see: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ProjectionExpressions.html
#
# For returning only certain items do:
# - For restricting Keys (primary (=partitions) or secondary (=sort)) key use KeyConditionExpression!
# - for further filtering the query use FilterExpression!
# 
# 


#
# returns JOBS of a user
# if field 'filter' is present in the body, jobs will be filtered.
# possible values:
# - 'active'
# - 'finished',
# - 'preliminary', 
# - deleted'
def doGetJobs(user_sub, body_json):
    if not 'filter' in body_json:
        filter_arr = []
        print("no filter in body, I set filter to empty")
    else:
        filter_arr = body_json.get('filter')

    db = boto3.resource('dynamodb', region_name=REGIONS.DEFAULT)
    table = db.Table(TABLES.JOBS)
    print(f"calling database with filter = {filter_arr}")

    # return ({'info filter': filter})
    try:
        if not filter_arr or filter_arr == []: # don't filter
            r = table.query(
                IndexName=JOBS.USER_SUB_INDEX,
                KeyConditionExpression=Key(JOBS.USER_SUB_ATTR).eq(user_sub)
                )
        else:
            # here we concatenate filters from filter_arr with || in a filter expression:
            # see: https://stackoverflow.com/a/39422244
            filter_exp = reduce(or_, (Key(JOBS.STATUS_ATTR).eq(el) for el in filter_arr))
            # filter_expression = map(lambda el: Key('status').eq(el), filter_arr)
            r = table.query(
                IndexName=JOBS.USER_SUB_INDEX,
                KeyConditionExpression=Key(JOBS.USER_SUB_ATTR).eq(user_sub),
                FilterExpression=filter_exp
                )

        items = r.get('Items')
        print(items)
        return items
    except ClientError as e:
        print(e)
        return { 'error': 'GET handler in doGetJobs' }


# main
def handlePathJobs(user_sub, method, body=''):
    if method == "POST":
        try:
            body_json = json.loads(body)
        except:
            return {'error': 'body not parseable as json'}

        if not 'action' in body_json:
            return {'error': 'action missing in body'}
        action = body_json.get('action')

        if action == 'get':
            return doGetJobs(user_sub, body_json)
        else:
            return {'error': 'invalid action'}

    elif method == "GET":
        return {'error': 'method GET not implemented'}
    else:
        return {'error': 'job handler didnt find method'}
