import json
import boto3
import os


def lambda_handler(event, context):
    print(event)

    ddb = boto3.resource('dynamodb')
    table = ddb.Table(os.environ['TABLE_NAME'])
    connect = boto3.client('connect')

