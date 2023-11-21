#resource "aws_dynamodb_table" "terraform_state_lock" {
#  name         = "stock-trading-lock" # Replace with your desired table name
#  billing_mode = "PAY_PER_REQUEST"      # You can adjust this as per your needs
#  hash_key     = "LockID"
#  attribute {
#    name = "LockID"
#    type = "S"
#  }
#}


#resource "aws_s3_bucket" "terraform_state_bucket" {
#  bucket = "stock-trading-state" # Replace with your desired bucket name
#
#}

terraform {
  backend "s3" {
    bucket         = "stock-trading-state" # Same as the S3 bucket name above
    key            = "trading-state"
    region         = "us-east-2" # Set your desired AWS region
#    encrypt        = true
    dynamodb_table = "stock-trading-lock"
  }
}
