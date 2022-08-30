import boto3

def create_orders_table(dynamodb):
    table = dynamodb.create_table(
        TableName='serverless-arch-example-orders',
        KeySchema=[
            {
                'AttributeName': 'request_id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'request_id',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 3,
            'WriteCapacityUnits': 3
        }
    )
    return table



if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    table = create_orders_table(dynamodb)
    print("Table status:", table.table_status)

    
    
