import json

from src import lambda_function


def test_lambda_handler():
    event = {
        "body": json.dumps(
            {
                "name": "onamae",
                "email": "onamae@example.com",
                "message": "案件全力でやります！",
            }
        )
    }
    context = None

    response = lambda_function.lambda_handler(event, context)

    # 基本構造の検証
    assert "statusCode" in response
    assert response["statusCode"] == 200

    # メッセージ内容の検証
    body = json.loads(response["body"])
    assert body.get("message") == "メール送信成功"
