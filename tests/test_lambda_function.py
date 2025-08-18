import json

import boto3
from botocore.stub import Stubber

from src import lambda_function

# Lambda側と同じ値を使う（DRYに保つ！）
SES_SENDER = "hata.kazuhiro@fieldwork48.com"  # SESで登録済みの送信元メール
SES_RECEIVER = "hata.kazuhiro@fieldwork48.com"  # 送信先メールアドレス
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
                "Subject": {"Data": "お問い合わせが届きました"},
                "Body": {
                    "Text": {
                        "Data": (
                            "名前: onamae\n"
                            "メールアドレス: test@emaail.com\n\n"
                            "メッセージ:\nめちゃ全力でやります！"
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
        "requestContext": {"http": {"method": "POST"}},
        "body": json.dumps(
            {
                "name": "onamae",
                "email": "test@emaail.com",
                "message": "めちゃ全力でやります！",
            }
        ),
    }

    # 実行 & レスポンス確認
    res = lambda_function.lambda_handler(event, None, ses_client=ses_client)

    body = json.loads(res["body"])

    assert res["statusCode"] == 200
    assert body["message"] == "メール送信成功"

    stubber.deactivate()
