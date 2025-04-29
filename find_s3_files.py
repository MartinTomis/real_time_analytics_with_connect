import json
import boto3
import os

s3 = boto3.client('s3')
BUCKET = 'transcribe-results-from-connect'

def lambda_handler(event, context):
    try:
        response = s3.list_objects_v2(Bucket=BUCKET)

        files = []
        for obj in response.get('Contents', []):
            files.append({
                'id': obj['Key'],
                'name': obj['Key']
            })

        return {
            'statusCode': 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            },
            'body': json.dumps(files)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({ 'error': str(e) })
        }
