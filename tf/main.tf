# main.tf
provider "aws" {
  region        = var.region
#  access_key    = var.AWS_ACCESS_KEY_ID
#  secret_key    = var.AWS_SECRET_ACCESS_KEY
#  session_token = var.AWS_SESSION_TOKEN
}

# Lambda
resource "aws_lambda_function" "trading_lambda" {
  function_name = var.function_name
  handler       = var.handler
  runtime       = var.runtime
  filename      = var.filename

  environment {
    variables = {
      PAPER_API_URL = var.PAPER_API_URL
      LIVE_API_URL  = var.LIVE_API_URL
      env           = var.env
    }
  }

  role = aws_iam_role.trading_role.arn
}

resource "aws_iam_policy" "cloudwatch_logs_policy" {
  name = var.logs_policy_name

  policy = var.cloudwatch_policy
}

resource "aws_iam_role" "trading_role" {
  name = var.role_name

  assume_role_policy = var.assume_role_policy

  inline_policy {
    name   = var.logs_policy_name
    policy = aws_iam_policy.cloudwatch_logs_policy.policy
  }
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.trading_lambda.function_name}"
}

resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name        = var.event_rule_name
  description = var.event_rule_description

  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "LambdaTarget"
  arn       = aws_lambda_function.trading_lambda.arn
}

resource "aws_lambda_permission" "cloudwatch_lambda_permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trading_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}


# SECRETS
resource "aws_secretsmanager_secret" "alpaca_trading_secrets" {
  name                    = var.secrets_manager_secret_name
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "alpaca_trading_secrets_curr" {
  secret_id      = aws_secretsmanager_secret.alpaca_trading_secrets.id
  secret_string  = jsonencode(var.alpaca_trading_secrets)
  version_stages = ["AWSCURRENT"]

  lifecycle {
    ignore_changes = [
      secret_string,
      version_stages
    ]
  }
}
resource "aws_secretsmanager_secret_version" "alpaca_trading_secrets_prev" {
  secret_id      = aws_secretsmanager_secret.alpaca_trading_secrets.id
  secret_string  = jsonencode(var.alpaca_trading_secrets)
  version_stages = ["AWSPREVIOUS"]

  lifecycle {
    ignore_changes = [
      secret_string,
      version_stages
    ]
  }
}

# PARAMS
resource "aws_ssm_parameter" "alpaca_trading_params" {
  count = var.region == "us-east-2" ? 1 : 0
  name  = var.param_store_name
  type  = "String"
  tier  = "Standard"
  value = jsonencode(
    {
      "PAPER_API_URL" = var.PAPER_API_URL,
      "LIVE_API_URL"  = var.LIVE_API_URL
    }
  )
}