import boto3
from boto3.dynamodb.conditions import Key
import os
import time

class DBHelper:
    def __init__(self) -> None:
        environment = os.environ['ENVIRONMENT']
        orders_table_name = os.environ['ORDERS_TABLE_NAME']
        
        if environment == "AWS_SAM_LOCAL":
            dynamodb_dev_uri = os.environ['DYNAMODB_DEV_URI']
            self.dynamodb = boto3.resource('dynamodb', endpoint_url=dynamodb_dev_uri)
        else:
            self.dynamodb = boto3.resource('dynamodb')
        
        self.orders_table = self.dynamodb.Table(orders_table_name)


    def update_order_status(self, request, status, location=None):
        return self.orders_table.put_item(
            Item={
                'request_id': request['request_id'],
                'url': request['url'],
                'status': status,
                'file_location': location,
                'epoch_time': int(time.time()),
            }
        )

    
    def get_order_status(self, request_id):
        response = self.get_records_by_key(self.orders_table, 'request_id', request_id)
        if 'Items' in response:
            return response['Items']
        return None
    
    def get_records_by_key(self, table, key, value):
        try:
            response = table.query(
                KeyConditionExpression=Key(key).eq(value)
            )
            return response
        except Exception as error:
            print(error)
            raise error
