import json

import boto3
from botocore.stub import Stubber

from src import lambda_function

# Lambda側と同じ値を使う（DRYに保つ！）
SES_SENDER = "hata.kazuhiro@fieldwork48.com"  # SESで登録済みの送信元メール
SES_RECEIVER = "hata.kazuhiro@fieldwork48.com"  # 送信先メール
SES_REGION = "ap-northeast-1"  # SESのリージョン


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
                "Subject": {"Data": "問い合わせが届きました"},
                "Body": {
                    "Text": {
                        "Data": (
                            "名前: onamae\n"
                            "メール: test@emaail.com\n"
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
                "email": "test@emaail.com",
                "message": "めちゃ全力でやります！",
            }
        )
    }

    # 実行 & レスポンス確認
    response = lambda_function.lambda_handler(event, None, ses_client=ses_client)

    body = json.loads(response["body"])

    assert response["statusCode"] == 200
    assert body["message"] == "メール送信成功"

    stubber.deactivate()
