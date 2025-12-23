provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "docs" {
  bucket = "ai-rag-docs-bucket"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-ai-rag-role"

  assume_role_policy = json.dumps({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policies" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_lambda_function" "doc_processor" {
  function_name = "document_processor"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.10"
  handler       = "app.lambda_handler"
  filename      = "document_processor.zip"
  timeout       = 300

  environment {
    variables = {
      OPENSEARCH_HOST = "your-opensearch-endpoint"
    }
  }
}

resource "aws_lambda_function" "query_handler" {
  function_name = "query_handler"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.10"
  handler       = "app.lambda_handler"
  filename      = "query_handler.zip"
  timeout       = 300

  environment {
    variables = {
      OPENSEARCH_HOST = "your-opensearch-endpoint"
    }
  }
}
