import json
import requests

TELEGRAM_TOKEN = '6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'

class COMMAND:
    welcome = '/start'
    help = '/help'
    run = '/run'
    kill = '/kill'

COMMAND_LIST = f"""
Commands:
{COMMAND.run}: run bot
{COMMAND.kill}: kill bot
"""

def send_telegram_message(text: str, chat_id: str) -> requests.models.Response:
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(TELEGRAM_API_URL + 'sendMessage', data=payload)

def lambda_handler(event, context):
    message = json.loads(event['body'])
    chat_id = str(message['message']['chat']['id']) # must convert to str!
    text = message['message']['text']

    if text in [COMMAND.welcome, COMMAND.help]:
        reply = COMMAND_LIST
    elif text ==  COMMAND.run:
        reply = 'To run bot'
    elif text ==  COMMAND.kill:
        reply = 'To kill bot'
    else:
        reply = f'Unknown command. Check {COMMAND.help}'

    send_telegram_message(reply, chat_id)
    return {
        'statusCode': 200
    }
