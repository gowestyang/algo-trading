import logging
import requests
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

API_TOKEN = '6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU'
CHAT_ID = '2069686152'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# This handler will be called when user sends `/start` or `/help` command
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")

# Funciton on message
@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(f"You said: {message.text}")

# Function on start of the bot
async def on_startup(dp):
    await bot.send_message(chat_id=CHAT_ID, text="Hello! Bot has been started.")

# Function on stop of the bot
async def on_shutdown(dp):
    await bot.send_message(chat_id=CHAT_ID, text="Bot has been stopped. Goodbye!")

if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)

    print("this line is excuted")
    
