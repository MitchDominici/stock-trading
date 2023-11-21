variable "region" {
  type        = string
  description = "The AWS region where the resources will be created."
}

variable "function_name" {
  type        = string
  description = "The name of the AWS Lambda function."
}

variable "handler" {
  type        = string
  description = "The entry point function for the Lambda function."
}

variable "runtime" {
  type        = string
  description = "The runtime environment for the Lambda function."
}

variable "filename" {
  type        = string
  description = "The file path to the Lambda deployment package."
}

variable "PAPER_API_URL" {
  type        = string
  description = "The URL for the Alpaca Paper Trading API."
}

variable "LIVE_API_URL" {
  type        = string
  description = "The URL for the Alpaca Live Trading API."
}

variable "logs_policy_name" {
  type        = string
  description = "The name of the IAM policy for CloudWatch Logs."
}

variable "role_name" {
  type        = string
  description = "The name of the IAM role for the Lambda function."
}

variable "assume_role_policy" {
  type        = string
  description = "The IAM policy document for assuming the Lambda execution role."
}

variable "cloudwatch_policy" {
  type        = string
  description = "The IAM policy document for CloudWatch permissions."
}

variable "event_rule_name" {
  type        = string
  description = "The name of the CloudWatch Events rule."
}

variable "event_rule_description" {
  type        = string
  description = "The description of the CloudWatch Events rule."
}

variable "schedule_expression" {
  type        = string
  description = "The schedule expression for triggering the Lambda function."
}

variable "secrets_manager_secret_name" {
  type        = string
  description = "The name of the AWS Secrets Manager secret."
}

variable "param_store_name" {
  type        = string
  description = "The name of the AWS Systems Manager Parameter Store parameter."
}

variable "env" {
  type        = map(string)
  description = "A map of environment variables for the Lambda function."
}

variable "alpaca_trading_secrets" {
  type        = object({
    PAPER_API_KEY    = string
    PAPER_API_SECRET = string
    LIVE_API_KEY     = string
    LIVE_API_SECRET  = string
  })
  description = "Configuration for Alpaca Trading secrets."
  default = {
    PAPER_API_KEY    = ""
    PAPER_API_SECRET = ""
    LIVE_API_KEY     = ""
    LIVE_API_SECRET  = ""
  }
}

variable "alpaca_trading_params" {
  type        = object({
    LIVE_API_URL  = string
    PAPER_API_URL = string
  })
  description = "Configuration for Alpaca Trading API URLs."
  default = {
    LIVE_API_URL  = ""
    PAPER_API_URL = ""
  }
}

#variable "AWS_ACCESS_KEY_ID" {
#  type        = string
#  description = "AWS Access Key ID for authentication."
#}
#
#variable "AWS_SECRET_ACCESS_KEY" {
#  type        = string
#  description = "AWS Secret Access Key for authentication."
#}
#
#variable "AWS_SESSION_TOKEN" {
#  type        = string
#  description = "AWS Session Token for temporary credentials."
#}
