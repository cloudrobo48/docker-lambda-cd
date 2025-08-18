import json
import logging

import boto3

SES_SENDER = "hata.kazuhiro@fieldwork48.com"
SES_RECEIVER = "hata.kazuhiro@fieldwork48.com"
SES_REGION = "ap-northeast-1"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.debug("Lambdaのデバッグログ開始")
logger.info("CI/CD Deploy Started in Global scope")


def lambda_handler(event, context, ses_client=None):
    try:
        method = (
            event.get("requestContext", {}).get("http", {}).get("method", "UNKNOWN")
        )
        logger.info(f"Lambda関数が呼び出された - メソッド: {method}")

        # OPTIONS リクエストへの対応（CORSプリフライト）
        if method == "OPTIONS":
            logger.info("OPTIONSリクエストに対するCORSレスポンスを返します")
            return {
                "statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": "",
            }

        # POST リクエストへの対応（メール送信）
        if method == "POST":
            if "body" in event and event["body"]:
                body = json.loads(event["body"])
            else:
                body = {}

            logger.info(f"受信したリクエストデータ: {body}")

            name = body.get("name", "No Name")
            email = body.get("email", "No Email")
            message = body.get("message", "No Message")

            logger.info(f"名前: {name}, メール: {email}, メッセージ: {message}")

            email_body = (
                f"名前: {name}\nメールアドレス: {email}\n\nメッセージ:\n{message}"
            )
            logger.info("メールの本文を作成")

            if ses_client is None:
                ses_client = boto3.client("ses", region_name=SES_REGION)

            logger.info("SESクライアントを作成")

            response = ses_client.send_email(
                Source=SES_SENDER,
                Destination={"ToAddresses": [SES_RECEIVER]},
                Message={
                    "Subject": {"Data": "お問い合わせが届きました"},
                    "Body": {"Text": {"Data": email_body}},
                },
            )

            logger.info(f"メール送信レスポンス: {response}")

            return {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "メール送信成功"}),
            }

        # その他のメソッドは拒否
        logger.warning(f"許可されていないHTTPメソッド: {method}")
        return {
            "statusCode": 405,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Method Not Allowed"}),
        }

    except Exception as e:
        logger.error(f"Lambda Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
