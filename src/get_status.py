from db import db_helper
import boto3
import json
import os
from botocore.exceptions import ClientError
from datetime import datetime

def lambda_handler(event=None, context=None):

    if event['httpMethod'] != "GET":
        return generate_response(404, "Invalid request method")

    query_params = event['queryStringParameters']

    if not validate_params(query_params):
        return generate_response(404, "Invalid request")
       
    try:
        dbHelper = db_helper.DBHelper()
        response = dbHelper.get_order_status(query_params['request_id'])
        print(response)
        if response is None or len(response) == 0:
            return generate_response(404, f"Request not found")

        presigned_url = None
        if response[0]['status'] == 'Complete':
            upload_bucket_name = os.environ['UPLOAD_BUCKET']
            presigned_url = create_presigned_url(upload_bucket_name, response[0]['file_location'])
        
        return generate_response(200, {
            "url": response[0]['url'],
            "request_id": response[0]['request_id'],
            "status": response[0]['status'],
            "updated": datetime.fromtimestamp(response[0]['epoch_time']).strftime('%Y-%m-%d %H:%M:%S'),
            "download_link": presigned_url
        })


    except Exception as e:
        print(e)
        return generate_response(500, f"Error processing request: {e}")

def generate_response(response_code, message):
    return {
        "statusCode": response_code,
        "body": json.dumps(message),
        "headers": { 
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*", 
            "Access-Control-Allow-Methods": "GET"
        }
    }

def validate_params(query_params):
    payload_valid = True
    # Check if required keys are in json_map
    keys_required = {'request_id'}
    for key in keys_required:
        if key not in query_params:
            payload_valid = False
            break

    # Check if all the values are strings
    return payload_valid        

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        return None

    # The response contains the presigned URL
    return response