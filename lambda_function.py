"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    should_end_session = False
    avg = get_averages()
    res = "Hey! I have your ergo scores for vision! Your recent score is "+str(avg[0])+" on 100. Your overall score is "+str(avg[1])+" on 100"
    return build_response(session_attributes, build_speechlet_response(card_title, res, None, should_end_session))
    
    
def getAverageToday():
    session_attributes = {}
    card_title = "Today's Score"
    should_end_session = False
    res = "Your ergo vision score for the day so far is "+str(get_averages()[0])+" on 100."
    return build_response(session_attributes, build_speechlet_response(card_title, res, None, should_end_session))
    
def getAverageOverall():
    session_attributes = {}
    card_title = "Overall Score"
    should_end_session = False
    res = "Your grand total for ergo vision score is "+str(get_averages()[1])+" on 100."
    return build_response(session_attributes, build_speechlet_response(card_title, res, None, should_end_session))
    
def getTips():
    session_attributes = {}
    card_title = "Tip of the day"
    should_end_session = False
    avg = get_averages()
    if (avg[2]>=100):
        res = "Hey! Why is that you keep staring at the sky? Stop looking up too often. Look straight!"
    else:
        res = "Hey! I understand that you're a humble person.. But no need to keep your head down all the time! Tell me.. is it that stupid phone of yours?"
    return build_response(session_attributes, build_speechlet_response(card_title, res, None, should_end_session))
    
    
def getPerformance():
    session_attributes = {}
    card_title = "Performance"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, get_performance(get_averages()[1]), None, should_end_session))

def get_averages():
    avg=0
    tavg=0
    aavg=0
    ttavg=0
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('alexa')
    response = table.scan()
    resCount = len(response['Items'])
    for idx, item in enumerate(response['Items']):
        val = int(item['id'].split('+',1)[1])
        aaavg = aavg+val
        if(val>100):
            v = 200-val
        else:
            v = val
        avg = avg+v
        if idx > resCount-5:
            tavg = tavg+v
            ttavg = ttavg + val
            
    return [tavg/5, avg/resCount, ttavg/5, aavg/resCount]
        
        
def get_performance(n):
    if(n>=90):
        return "Wow you're the best! Keep up the ergonomic spirit!"
    elif(n>80):
        return "Great ergonomics! A little more care would take you to the top!"
    elif(n>=75):
        return "You're safe... But there's a lot of scope for care and imporvement"
    else:
        return "Uh oh... I don't see good stats here! You have to buckle up and get your ergonomic score up!"        

    

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))



# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AverageToday":
        return getAverageToday()
    elif intent_name == "AverageOverall":
        return getAverageOverall()
    elif intent_name == "Performance":
        return getPerformance()
    elif intent_name == "Tips":
        return getTips()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
