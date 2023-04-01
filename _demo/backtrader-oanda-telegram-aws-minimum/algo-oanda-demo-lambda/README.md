# algo-oanda-demo-lambda

Deploy AWS Lambda function to control the docker container.

## Steps
1. In AWS Lambda, create a Lambda function.
    * Runtime: Python 3.9
    * Permissions: "Create a new role with basic Lambda permissions" (or use an existing role with the right permissions)
    * Advanced Setting: None
2. Deploy Lambda function - see section below.
    * Update permission of the Lambda function to allow updating ECS service - see below.
3. In AWS API Gateway, deploy a REST API and link it to the Lambda function. This is needed for telegram to trigger the lambda via webhook.
    * Build a new REST API
    * Create Method - ANY
        * Integration Type: Lambda Function
        * Use Lambda Proxy integration - tick
        * Select your Lambda function
        * Use Default TImeout - tick
    * Deploy API - give it a tag, such as "v1"
    * After deployment, note down the invoke URL, such as `https://opqqjgl1x2.execute-api.us-east-1.amazonaws.com/v1/`
        * You can always find it in Dashboard
4. Set webhook to the telegram bot by `https://api.telegram.org/bot<your-bot-token>/setWebHook?url=<your-API-invoke-URL>`
    * For example, `https://api.telegram.org/bot6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU/setWebHook?url=https://opqqjgl1x2.execute-api.us-east-1.amazonaws.com/v1/`
    * You can do this simply using a web browser
    * check webhook: `https://api.telegram.org/bot6252951396:AAHAYGHvDR_r1TKmC1x9Exxs93ygYJf8sPU/getWebhookInfo`

<br>

## Deploy Lambda
1. At local computer
    * conda create -n telegram-lambda-py39 python=3.9
    * conda activate telegram-lambda-py39
2. At the deployment-package folder
    * pip install --target ./ requests
3. Copy `lambda_function.py` to the deployment-package folder
4. zip all contents in the deployment-package folder
5. At AWS web console, upload the zip file.

<br>

## Update Lambda Permissions
* Use a new role for the Lambda function
* In IAM, add permissions to the role:
```
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeServices",
        "ecs:UpdateService"
      ],
      "Resource": [
        "*"
      ]
    }
```

<br>

## Reference
* https://chatbotslife.com/building-a-telegram-bot-with-aws-api-gateway-and-aws-lambda-21ef3239a053
