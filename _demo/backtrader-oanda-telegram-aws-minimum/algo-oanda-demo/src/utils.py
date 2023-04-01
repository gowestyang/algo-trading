import logging
import json
import requests

# logger
LOGGING_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"
LOGGING_LEVEL = logging.INFO
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
logger = logging.getLogger(__name__)

# telegram
TELEGRAM_CONFIG_FILE = 'src/config/telegram.json'
with open(TELEGRAM_CONFIG_FILE) as f:
    d_telegram_config = json.load(f)

TELEGRAM_TOKEN = d_telegram_config['telegram_api_token']
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
CHAT_ID = d_telegram_config['telegram_chat_id']

# Function to send a message to telegram
def send_telegram(text: str, chat_id: str=CHAT_ID) -> requests.models.Response:
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(TELEGRAM_API_URL + 'sendMessage', data=payload)

# Function to log and send a message to telegram
def send_log(text: str, level=logging.INFO) -> None:

    logger.log(msg=text, level=level)
    
    if level > logging.DEBUG:
        response = send_telegram(text)
        if response.status_code != 200:
            logger.log(f"WARNING: failed to send message to telegram: {response.text}", level=logging.warning)
