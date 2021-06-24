import json
import boto3
import os
import datetime
from dateutil.parser import parse

connect = boto3.client('connect')
instance_id = os.environ['INSTANCE_ID']
contact_flow_id = os.environ['CONTACT_FLOW_ID']
source_phone = os.environ['SOURCE_PHONE']

def lambda_handler(event, context):
    print('Evento:', event)

    ddb = boto3.resource('dynamodb')
    table = ddb.Table(os.environ['TABLE_NAME'])
    employees = table.scan()['Items']


    ''' 
    ejemplo de item
    {
        "EmployeeID": "82a9b509-0a9b-4ed4-adf6-3ae8846b747d",
        "FirstName": "Enrique",
        "LastName": "Rodriguez",
        "CallWindowStart": "2021-05-07T00:05:00+00:00",
        "CallWindowEnd": "2021-05-07T00:05:00+00:00",
        "Calling": false,
        "Completed": false,
        "PhoneNumber": "+56974769647"
    }
    '''

    to_call = []
    now = datetime.datetime.now().astimezone()
    for employee in employees:
        start_window = parse(employee['CallWindowStart'])
        end_window = parse(employee['CallWindowEnd'])
        window_ok = (now > start_window) and (now < end_window) 
        status_ok =  (employee['Calling'] == False) and (employee['Completed'] == False)
        if (window_ok) and (status_ok):
            to_call.append(employee)

    print ('to call:', to_call)
    for empl in to_call:
        response = call_employee(empl)
        if response:
            empl['Calling'] = True
            table.put_item(Item=empl)


def call_employee(empl):
    print ('calling... ',empl['FirstName'], empl['PhoneNumber'] )
    try:
        response = connect.start_outbound_voice_contact(
            DestinationPhoneNumber=empl['PhoneNumber'],
            ContactFlowId=contact_flow_id,
            InstanceId=instance_id,
            SourcePhoneNumber=source_phone,
            Attributes={
                'EmployeeID': empl['EmployeeID'],
                'Name': empl['FirstName']
            }
        )
        print (response['ResponseMetadata']['HTTPStatusCode'])
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        
        return False
    except Exception:
        return False

