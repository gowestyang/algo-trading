# backtrader-oanda-telegram-aws-minimum

This project demonstrates how to deploy a simple trading bot with
* Strategy coded with Backtrader
* Trade executed by Oanda demo account
* Bot deployed on AWS as a container
* Bot controlled by Telegram via AWS Lambda

Features
* The user can run / stop the trading bot by sending messages in Telegram chat.
* The message will trigger AWS Lambda function via webhook.
* The AWS Lambda function will start / stop the container.
* While running, the container hosts logic to trade automatically.
