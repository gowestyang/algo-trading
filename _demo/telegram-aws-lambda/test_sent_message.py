import json
import requests

TELEGRAM_TOKEN = '6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'

def send_telegram_message(text, chat_id='2069686152'):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(TELEGRAM_API_URL + 'sendMessage', data=payload)

response = send_telegram_message('from python')
print(type(response))
