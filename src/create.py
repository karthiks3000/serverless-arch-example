import json
from db import db_helper
import boto3
import os

def lambda_handler(event, context):

    if event['httpMethod'] != "POST":
        return generate_response(404, "Invalid request method")

    request = json.loads(event['body'])
    if not validate_payload(request):
        return generate_response(404, "Invalid payload")

    # use lambda request id for better tracking purposes
    request['request_id'] = context.aws_request_id
    request_json = json.dumps(request)
    print(f"Processing request with Request Id: {request['request_id']}")

    try:
        dbHelper = db_helper.DBHelper()
        dbHelper.update_order_status(request=request, status='Created')

        sqs = boto3.client('sqs')
        sqs_queue = os.environ['SQS_QUEUE']
        print(f"Sending request to the Queue")

        request_json = json.dumps(request)
        response = sqs.send_message(
            QueueUrl=sqs_queue,
            MessageBody=request_json
        )

        if 'MD5OfMessageBody' in response:
            dbHelper.update_order_status(request=request, status='Queued')
            return generate_response(200, request_json)
        else:
            print(f'Error sending request to queue: {response}')
            return generate_response(500, f"Error sending request to queue: {response}")

    except Exception as e:
        print(e)
        return generate_response(500, f"Error processing request: {e}")


def validate_payload(json_map):
    keys = json_map.keys()
    payload_valid = True

    # Check if required keys are in json_map
    keys_required = {'url'}
    for key in keys_required:
        if key not in keys:
            payload_valid = False
            break
    
    if str(json_map['url']).strip() == '':
        return False

    return payload_valid   

def generate_response(response_code, message):
    return {
        "statusCode": response_code,
        "body": message,
        "headers": { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
            "Access-Control-Allow-Methods": "POST" 
        }
    }