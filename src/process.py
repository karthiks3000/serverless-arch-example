import json
import time
from db import db_helper
from selenium.webdriver.common.by import By
from web_driver_wrapper import WebDriverWrapper
from io import StringIO
import boto3
import csv
import os
from datetime import datetime

def lambda_handler(event=None, context=None):
    request = get_request(event=event)
    if request is None:
        return {
            "statusCode": 400,
            "body": {
                "message": "Cannot parse url"
            }
        }
    
    dbHelper = db_helper.DBHelper()
    try:
        dbHelper.update_order_status(request=request, status='In Progress')

        url = request['url']
        upload_bucket_name = str(os.environ['UPLOAD_BUCKET'])
        result_list = []
        with WebDriverWrapper() as driver_wrapper:
            driver = driver_wrapper.driver
            driver.get(url)
            search_results = driver.find_elements(By.XPATH, "//div[@data-header-feature]")
            for result in search_results:
                result_list.append({"result": result.text})

        if len(result_list) > 0:
            dt_string = datetime.now().strftime("%Y-%m-%d_%H%M")
            csv_file_name =  f'export_{dt_string}.csv'
            upload_csv_s3(result_list, upload_bucket_name, csv_file_name)
            dbHelper.update_order_status(request=request, status='Complete', location=csv_file_name)
        else:
            dbHelper.update_order_status(request=request, status='No Results')

    except Exception as e:
        print(e)
        dbHelper.update_order_status(request=request, status='Failed')
        return {
            "statusCode": 500,
            "body": {
                "message": f"Error processing request: {e}"
            }
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "records found": len(result_list),
            }
        ),
    }

def get_request(event) -> str:
    if "Records" in event:
        body = event['Records'][0]['body']
        event = json.loads(body)
    return event


def upload_csv_s3(data_dictionary,s3_bucket_name,csv_file_name):
    print('Starting csv upload to S3')
    try:
        data_dict_keys = data_dictionary[0].keys()
        
        # creating a file buffer
        file_buff = StringIO()
        
        # writing csv data to file buffer
        writer = csv.DictWriter(file_buff, fieldnames=data_dict_keys)
        writer.writeheader()
        writer.writerows(data_dictionary)
            
        # creating s3 client connection
        client = boto3.client('s3')
        
        # placing file to S3, file_buff.getvalue() is the CSV body for the file
        client.put_object(Body=file_buff.getvalue(), Bucket=s3_bucket_name, Key=csv_file_name)
        print('Completed uploading to S3')
    except Exception as e:
        print(e)
        raise e