import time
import requests

TELEGRAM_TOKEN = '6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU'
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
CHAT_ID = '2069686152'

def send_telegram_message(text: str, chat_id: str) -> requests.models.Response:
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(TELEGRAM_API_URL + 'sendMessage', data=payload)


if __name__ == '__main__':

    while(True):
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        send_telegram_message(t, chat_id=CHAT_ID)
        time.sleep(5)
