import json

import boto3
from moto import mock_ses  # ← ここを修正

from src import lambda_function

# Lambda側で使ってる定数と合わせる（テスト用に同じ値にしておく）
# SES の設定
SES_SENDER = "hata.kazuhiro@fieldwork48.com"  # SESで登録済みの送信元メール
SES_RECEIVER = "hata.kazuhiro@fieldwork48.com"  # 送信先メール
SES_REGION = "ap-northeast-1"  # SESのリージョン


@mock_ses
def test_lambda_handler():

    # SESモック空間を発生させる
    client = boto3.client("ses", region_name=SES_REGION)

    # SESに送信元メールアドレスを“検証済み”として登録（これが無いとモックでもエラー出る）
    client.verify_email_identity(EmailAddress=SES_SENDER)

    # Lambdaへ渡すイベント
    event = {
        "body": json.dumps(
            {
                "name": "onamae",
                "email": SES_RECEIVER,
                "message": "めちゃ全力でやります！",
            }
        )
    }
    context = None

    # Lambda関数を実行
    response = lambda_function.lambda_handler(event, context)

    # レスポンスの構造確認
    assert "statusCode" in response
    assert response["statusCode"] == 200

    # メッセージ内容の検証
    body = json.loads(response["body"])
    assert body.get("message") == "メール送信成功"
