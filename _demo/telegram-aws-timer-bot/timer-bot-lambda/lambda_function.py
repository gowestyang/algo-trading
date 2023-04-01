import json
import requests
import boto3

# ECS configurations
CLUSTER_NAME = 'DevBot'
SERVICE_NAME = 'telegram-timer-bot-service'

ECS = boto3.client('ecs')

# Telegram configurations
TELEGRAM_TOKEN = '6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'

# Telegram commands
class COMMAND:
    welcome = '/start'
    help = '/help'
    debug = '/debug'
    run = '/run'
    kill = '/kill'

COMMAND_LIST = f"""
Commands:
{COMMAND.run}: run bot
{COMMAND.kill}: kill bot
"""

# ECS functions
def start_ecs_service() -> dict:
    d_response = ECS.update_service(cluster=CLUSTER_NAME, service=SERVICE_NAME, desiredCount=1)
    return d_response

def stop_ecs_service() -> dict:
    d_response = ECS.update_service(cluster=CLUSTER_NAME, service=SERVICE_NAME, desiredCount=0)
    return d_response

def restart_ecs_service() -> dict:
    d_response = stop_ecs_service()
    d_response = start_ecs_service()
    return d_response

def send_telegram_message(text: str, chat_id: str) -> requests.models.Response:
    """ Function to send a message to telegram chat """
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(TELEGRAM_API_URL + 'sendMessage', data=payload)

def lambda_handler(event: dict, context) -> dict:
    """ AWS Lambda hanlder """

    message = json.loads(event['body'])
    chat_id = str(message['message']['chat']['id']) # must convert to str!
    text = message['message']['text']

    d_response = None
    if text in [COMMAND.welcome, COMMAND.help]:
        reply = COMMAND_LIST
    elif text ==  COMMAND.run:
        reply = 'To run bot'
        d_response = start_ecs_service()
    elif text ==  COMMAND.kill:
        reply = 'To kill bot'
        d_response = stop_ecs_service()
    elif text == COMMAND.debug:
        reply = f'DEBUG: {d_response}'
    else:
        reply = f'Unknown command. Check {COMMAND.help}'

    send_telegram_message(reply, chat_id)
    return {
        'statusCode': 200
    }
