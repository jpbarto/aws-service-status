"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import logging
from datetime import datetime
import awsstatusdata as awsdata

logger = logging.getLogger('AWSStatusSkill')
logger.setLevel(logging.DEBUG)

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
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the AWS Service Status checker. " \
                    "Please ask for the status of any AWS service or " \
                    "the historical availability of any service."

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask for the status of an AWS service."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the AWS Service Status checker. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def get_service_status(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    service = None
    region = None

    if 'service' in intent['slots'] and 'value' in intent['slots']['service']:
        service = intent['slots']['service']['value']

    if 'region' in intent['slots'] and 'value' in intent['slots']['region']:
        region = intent['slots']['service']['value']
            
    if not awsdata.in_service_map (service):
        speech_output = "I didn't recognize the service name {}, can you please repeat your question?".format (service)
        reprompt_text = speech_output
    elif region is not None and not awsdata.in_region_map (region):
        speech_output = "I didn't understand what region you're asking about, can you please repeat your question?"
        reprompt_text = speech_output
    else:
        issues = awsdata.get_service_issues(service, region)

        speech_output = "There are currently {} issues related to the {} service.".format(len(issues['current']), service)
        reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def get_service_availability(intent, session):
    session_attributes = {}
    reprompt_text = None

    if 'service' in intent['slots'] and 'value' in intent['slots']['service']:
        service = intent['slots']['service']['value']
        region = None
        if 'region' in intent['slots'] and 'value' in intent['slots']['region']:
            region = intent['slots']['region']['value']

        issues = awsdata.get_service_issues(service, region)
        current_issues = issues['current']
        archived_issues = issues['archived']
        issue_count = len(current_issues) + len(archived_issues)
        uptime = int(((awsdata.archive_length - issue_count) /
                      awsdata.archive_length) * 100)
        region_text = "globally"
        if region is not None:
            region_text = "in {}".format(region)
        speech_output = "The {} service has demonstrated {} an uptime of {} percent over the last {} days.".format(
            service, region_text, uptime, awsdata.archive_length)
        if uptime < 100:
            speech_output += " The service is currently experiencing {} issue".format(len(current_issues))
            if len(current_issues) != 1:
                speech_output += "s"

            speech_output += " and has had {} historical issue".format(len(archived_issues))
            if len(archived_issues) != 1:
                speech_output += "s"

            if len(archived_issues) > 0:
                speech_output += ". Historically the issues experienced include:"

                for i in range(len(archived_issues)):
                    if i > 2:
                        break
                    issue = archived_issues[i]
                    speech_output += " On {} in {} there was {}. ".format(datetime.fromtimestamp(
                        issue['date']).strftime('%d %B %Y'), issue['region_code'], issue['summary'])

        should_end_session = True
    else:
        speech_output = "I am not sure what service your asking about."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """
    awsdata.create_service_map ()
    awsdata.refresh_issues()

    logger.debug("on_session_started requestId=" + session_started_request['requestId']
                 + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    logger.debug("on_launch requestId=" + launch_request['requestId'] +
                 ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    logger.debug("on_intent requestId=" + intent_request['requestId'] +
                 ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "StatusIntent":
        return get_service_status(intent, session)
    elif intent_name == "AvailabilityIntent":
        return get_service_availability(intent, session)
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
    logger.debug("on_session_ended requestId={0}, sessionId={1}".format(
        session_ended_request['requestId'], session['sessionId']))
    # add cleanup logic here


# --------------- Main handler ------------------

def handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    logger.debug("event.session.application.applicationId={0}".format(
        event['session']['application']['applicationId']))

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started(
            {'requestId': event['request']['requestId']}, event['session'])

    if awsdata.archive_length == 0:
        awsdata.create_service_map ()
        awsdata.refresh_issues()
    logger.debug ("Prepared with {} known services and {} known regions".format (len (awsdata.service_map), len (awsdata.region_map)))
    logger.debug ("Tracking {} current and {} historical issues".format (len (awsdata.current_issues), len (awsdata.archived_issues)))

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
