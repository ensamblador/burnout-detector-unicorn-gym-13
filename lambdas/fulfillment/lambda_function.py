import math
import dateutil.parser
import datetime
import time
import os
import logging
import boto3
#Libraries for DynamoDB
import json
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import unicodedata
from datetime import datetime



#Libraries for Connect
#client = boto3.client('connect')

#Logger Functions
#logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)

#DynamoDB_Table = "EmployeeResponses"
DynamoDB_Table  = os.environ['DynamoDB_Table']

# Creating the DynamoDB Client
clientdb = boto3.client('dynamodb')
dyndb_resource = boto3.resource('dynamodb')
table = dyndb_resource.Table(DynamoDB_Table)

# Initialize SNS client
#clientsns = boto3.client('sns')


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


""" --- Functions that control the bot's behavior --- """
def getBurnoutScore(intent_request):
    
    """
    Performs dialog management and returns LexResponse
    """
    
    #Variables for the function
    valid_response = None
    burnout_score = 0
    Lex_content_response = "There was an error processing your input information"
    
    lex_one = try_ex(lambda: get_slots(intent_request)['slotOne'])
    lex_two = try_ex(lambda: get_slots(intent_request)['slotTwo'])
    lex_three = try_ex(lambda: get_slots(intent_request)['slotThree'])
    lex_four = try_ex(lambda: get_slots(intent_request)['slotFour'])
    lex_five = try_ex(lambda: get_slots(intent_request)['slotFive'])
    lex_six = try_ex(lambda: get_slots(intent_request)['slotSix'])
    
    burnout_score = calculateScore (lex_one, lex_two, lex_three, lex_four, lex_five, lex_six)
    
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    client_EmployeeID = intent_request["sessionAttributes"]["EmployeeID"]
    
    #put item in DynamoDB
    lex_stage = intent_request["invocationSource"]

    
    if lex_stage == 'FulfillmentCodeHook':
    
        responseDB = clientdb.put_item(
        TableName=DynamoDB_Table,
        Item={
            'EmployeeID': {"S": client_EmployeeID },
            'ResponseDate': {"S": current_time },
            'lex_one': {"S": lex_one },
            'lex_two': {"S": lex_two },
            'lex_three': {"S": lex_three },
            'lex_four': {"S": lex_four },
            'lex_five': {"S": lex_five },
            'lex_six': {"S": lex_six },
            'burnout_score': {"N": str(burnout_score) }
            
        })
    
    
    
    print("Score", burnout_score)
    
    if burnout_score > 25:
        Lex_content_response = "LEVEL 5. Your score was " + str(burnout_score) + " we suggest that you reach your manager to start discussing as soon as possible alternatives to reduce you stress of working from home."
    
    if (burnout_score >20 and burnout_score < 25):
        Lex_content_response = "LEVEL 4. Your score was " + str(burnout_score) + " we suggest that you reach your manager to start discussing alternatives to reduce you stress of working from home."

    if (burnout_score >15 and burnout_score < 20):
        Lex_content_response = "LEVEL3 .Your score was " + str(burnout_score) + " we suggest that you consider some alternatives to reduce you stress of working from home."
        
    if (burnout_score >10 and burnout_score < 15):
        Lex_content_response = "LEVEL 2. Your score was " + str(burnout_score) + " we suggest that you continue with this balance in your work and home."
        
    if (burnout_score >0 and burnout_score < 10):
        Lex_content_response = "LEVEL 1. Your score was " + str(burnout_score) + " we suggest that you keep up the good work"
    
    if (burnout_score < 0 ):
        Lex_content_response = "ERROR " +  str(burnout_score) + "There was an error processing your answers. Please try again "
    
    
    print (Lex_content_response)
          
    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
#                  'content': Lex_content_response })
                  'content': 'Gracias' })
""" --- Intents --- """
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    #logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))
    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
#    if intent_name == 'Burnout':
#        return getBurnoutScore(intent_request)
    if intent_name == 'yes_intent':
            return getBurnoutScore(intent_request)
        
    #if intent_name == 'Menu':
    #    return getMenu(intent_request)

    raise Exception('Intento con nombre ' + intent_name + ' no soportada actualmente')


""" --- Main handler --- """
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    
    print("Event: ",  event)
    
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    #logger.debug('event.bot.name={}'.format(event['bot']['name']))
    return dispatch(event)
    
    
def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None
        

def safe_int(n):
    """
    Safely convert n value to int.
    """
    
    if n is not None:
        return int(n)
    return n
    
    
    
#def utc_to_local(utc_dt):
#    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    
def exists_in_DynDB_v2 (dyndbtablename, primary_column_to_search, primary_key_to_search):
    
    table = dyndb_resource.Table(dyndbtablename)
    try:
        response = try_ex(lambda: table.get_item(Key={primary_column_to_search: primary_key_to_search}))
    except:
        return None
    else:
        return response
        

# Return total Score
def calculateScore(one, two, three, four, five, six):
    
    total_score = safe_int(return_value(one)) + safe_int(return_value(two)) +safe_int(return_value(three)) + safe_int(return_value(four)) + safe_int(return_value(five)) + safe_int(return_value(six))
    
    return total_score
    

# Return value for each lexslot
def return_value (value):
    
    value = value.lower()
    
    print("Value: ", str(value))
    score=-50
    

    if (value == "siempre"):
        score = 5
#    if (value == "often"):
#        score = 4
    if (value == "a veces"):
        score = 3
#    if (value == "rarely"):
#        score = 2
    if (value == "nunca"):
        score = 1    
        
    return score