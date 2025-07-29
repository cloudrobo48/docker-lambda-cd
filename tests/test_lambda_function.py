import json

import boto3
from botocore.stub import Stubber

from src import lambda_function

# Lambda側と同じ値を使う（DRYに保つ！）
SES_SENDER = lambda_function.SES_SENDER
SES_RECEIVER = lambda_function.SES_RECEIVER
SES_REGION = lambda_function.SES_REGION


def test_lambda_handler():
    # SESクライアント＆スタブの準備
    ses_client = boto3.client("ses", region_name=SES_REGION)
    stubber = Stubber(ses_client)

    # Lambdaが呼び出す send_email の期待リクエスト & ダミーレスポンス
    stubber.add_response(
        "send_email",
        {"MessageId": "dummy-message-id"},
        {
            "Source": SES_SENDER,
            "Destination": {"ToAddresses": [SES_RECEIVER]},
            "Message": {
                "Subject": {"Data": "お問い合わせありがとうございます"},
                "Body": {
                    "Text": {
                        "Data": (
                            "名前: onamae\n"
                            "メール: hata.kazuhiro@fieldwork48.com\n"
                            "内容: めちゃ全力でやります！"
                        )
                    }
                },
            },
        },
    )
    stubber.activate()

    # Lambda関数にSESクライアントを差し込む（依存注入が前提）
    lambda_function.ses_client = ses_client

    # Lambdaのeventを定義
    event = {
        "body": json.dumps(
            {
                "name": "onamae",
                "email": SES_RECEIVER,
                "message": "めちゃ全力でやります！",
            }
        )
    }

    # 実行 & レスポンス確認
    response = lambda_function.lambda_handler(event, None)
    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["message"] == "メール送信成功"

    stubber.deactivate()
