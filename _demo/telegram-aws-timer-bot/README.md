# telegram-aws-timer-bot

This project demonstrates how to deploy a simple Telegram timer bot, as a docker container, using AWS Lambda and AWS ECS.

Funcitons
* The user can run / stop the timer bot by sending messages in Telegram chat.
* The message will trigger AWS Lambda function via webhook.
* The AWS Lambda function will start / stop the container.
* While running, the container will send current time to the Telegram chat every 5 sec.
