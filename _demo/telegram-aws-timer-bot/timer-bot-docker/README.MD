# timer-bot-docker

Need to have docker desktop installed and running.

<br>

## Build Docker Image
* docker build --tag telegram-timer-bot .

<br>

## (For Info) Manage Docker Images
* docker images
* docker tag telegram-timer-bot:latest telegram-timer-bot:v1.0.0
* docker rmi telegram-timer-bot:v1.0.0

<br>

## (For Info) Run/Stop Docker Images
* docker run -d --name telegram-bot-1 telegram-timer-bot
    * `-d` is detached for running in background
    * `--name` is to give the container a name
* docker ps -a
* docker stop telegram-bot-1
* docker restart telegram-bot-1
* docker rm telegram-bot-1

<br>

## Push to AWS
View "Push Instruction" from AWS ECR web console.
