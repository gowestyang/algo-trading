# algo-oanda-demo

Build docker image and push to AWS.

<br>

## Environment Setup
* conda create -n algo-oanda-demo-py38 python=3.8
* conda activate algo-oanda-demo-py38
* pip install -r requirements.txt
* pip install git+https://github.com/happydasch/btoandav20

<br>

## (For Info) Remove Conda Env
* conda deactivate
* conda env remove -n algo-oanda-demo-py38

<br>

## Build Docker Image
* docker build --tag algo-oanda-demo .

## (For Info) Manage Docker Image
* docker images
* docker tag algo-oanda-demo:latest algo-oanda-demo:v1.0.0
* docker rmi algo-oanda-demo:v1.0.0

<br>

## Run/Stop Docker Images
* docker run -d --name algo-1 algo-oanda-demo
    * `-d` is detached for running in background
    * `--name` is to give the container a name
* docker ps -a
* docker stop algo-1
* docker restart algo-1
* docker rm algo-1

<br>

## Push to AWS
View "Push Instruction" from AWS ECR web console.
