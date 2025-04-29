import json
import boto3
import os
from botocore.client import Config

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


channel_dict = {'ch_0': 'CLIENT', 'ch_1': 'AGENT'}
sentiment_score_dict = {'POSITIVE':1, 'NEGATIVE':-1, 'NEUTRAL':0, 'MIXED': 0}
session = boto3.session.Session()

bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
bedrock_client = boto3.client('bedrock-runtime', region_name = "eu-central-1")
client_comprehend = boto3.client('comprehend', region_name='eu-central-1')
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

def identify_language(v_cz, channel_lang_map):
    ## Loop through all items
    
    channel_list = []
    
    # ch_0:
    if channel_lang_map['ch_0'] == 'en':
        for channel in v_cz['results']['channel_labels']['channels']:
            if channel['channel_label'] == 'ch_0':
                channel_list.append(channel)

    if channel_lang_map['ch_1'] == 'en':
        for channel in v_cz['results']['channel_labels']['channels']:
            if channel['channel_label'] == 'ch_1':
                channel_list.append(channel)


            
    conversation_dictionary = {}
    for channel in channel_list:
        channel_label = channel['channel_label']
        for item in channel['items']:
            if item['type'] == 'pronunciation':
                start_time = item['end_time']
                conversation_dictionary[item['start_time']]=item
            else:
                conversation_dictionary[start_time]=item
                
    return conversation_dictionary

def print_conversation(conversation_dict_, channel_dict_):
    sorted_dictionary = sorted(conversation_dict_.items(), key = lambda kv: float(kv[0]))
    
    starting_label = sorted_dictionary[0][1]['channel_label']
    
    conversation_all = ''
    
    phrase = ''
    for speech in sorted_dictionary:
        channel_label = speech[1]['channel_label']
        if channel_label == starting_label:
            if speech[1]['type'] == 'pronunciation':
                phrase += ' ' + speech[1]['alternatives'][0]['content']
            else:
                phrase += speech[1]['alternatives'][0]['content'] 
        else:
            #print('{}: {}'.format(channel_dict_[starting_label], phrase))
            conversation_all += '{}: {}'.format(channel_dict_[starting_label], phrase) + '\n'

            phrase = speech[1]['alternatives'][0]['content']
            starting_label = channel_label
            #conversation_all += '{}: {}'.format(channel_dict_[starting_label], phrase) + '\n'
    print(conversation_all)    
    return conversation_all

def calculate_sentiment(list_of_conversation_, sentiment_score_dict_, client_comprehend_):

    sentiment_score_all = 0
    sentiment_score_agent = 0
    sentiment_score_client = 0


    counter_agent = 0
    counter_client = 0

    for i, line in enumerate(list_of_conversation_):

        if 'CLIENT' in line:
            message_type = 'client'
            counter_client +=1
        if 'AGENT' in line:
            message_type = 'agent'
            counter_agent += 1



        line = line.replace('AGENT: ', '')
        line = line.replace('CLIENT: ', '')


        response = client_comprehend_.detect_sentiment(

            Text=line,
            LanguageCode='en'
        )
        sentiment = sentiment_score_dict_[response['Sentiment']]

        sentiment_score_all += sentiment
        if message_type == 'client':
            sentiment_score_client += sentiment
        elif message_type == 'agent':
            sentiment_score_agent += sentiment


    return sentiment_score_all/(i+1), sentiment_score_agent/(counter_agent), sentiment_score_client/(counter_client)

s3 = boto3.client('s3')
BUCKET_NAME = "transcribe-results-from-connect"

def lambda_handler(event, context):
    
    logger.info("EVENT RECEIVED: %s", json.dumps(event))
    try:
        raw_body = event.get('body', '{}')
        body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

        #body = json.loads(event.get('body', '{}'))
        file_id = body.get('fileId')

        if not file_id:
            return {
                "statusCode": 400,
                "body": json.dumps({ "error": "Missing 'fileId'" })
            }

        # Get file content from S3
        s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=file_id)
        file_content = s3_object['Body'].read().decode('utf-8')

        #####
        json_contents_cz = json.loads(file_content)
        transcript_ = json_contents_cz['results']['transcripts'][0]['transcript']
        logger.info("EVENT RECEIVED: %s", transcript_)
        
        lang_map = {'ch_0': 'en', 'ch_1': 'en'}
        conversation_dictionary = identify_language(json_contents_cz, lang_map)
        transcript = print_conversation(conversation_dictionary, channel_dict)
        logger.info("EVENT RECEIVED: %s", transcript)
        print(transcript)
        #print('Prompt: {}'.format(call_llm(prompt, transcript, bedrock_client, model_id )))
        #####

        conversation_list = transcript.splitlines()

        sentiment_score_all, sentiment_score_agent, sentiment_score_client = calculate_sentiment(conversation_list, sentiment_score_dict, client_comprehend)


        # Process with your search function
        #answer = search_function(file_content, question)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({ "summary": transcript, "sentiment_all": sentiment_score_all, "sentiment_agent": sentiment_score_agent, "sentiment_client": sentiment_score_client })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({ "error": str(e) })
        }
