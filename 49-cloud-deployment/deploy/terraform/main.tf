# Read-along: never applied in this course. It creates in AWS what the module's programs create in moto.

terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# ---- S3: snapshots and results ---------------------------------------------------------------

resource "aws_s3_bucket" "runs" {
  bucket = var.bucket_name

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "runs" {
  bucket = aws_s3_bucket.runs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "runs" {
  bucket                  = aws_s3_bucket.runs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ---- The image -------------------------------------------------------------------------------

resource "aws_ecr_repository" "solver" {
  name                 = "gridcap-solver"
  image_tag_mutability = "IMMUTABLE"
}

# ---- Roles -----------------------------------------------------------------------------------

data "aws_iam_policy_document" "assume" {
  for_each = toset(["batch.amazonaws.com", "ecs-tasks.amazonaws.com", "states.amazonaws.com", "lambda.amazonaws.com"])
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = [each.value]
    }
  }
}

resource "aws_iam_role" "batch_service" {
  name               = "gridcap-batch-service"
  assume_role_policy = data.aws_iam_policy_document.assume["batch.amazonaws.com"].json
}

resource "aws_iam_role_policy_attachment" "batch_service" {
  role       = aws_iam_role.batch_service.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole"
}

resource "aws_iam_role" "solve_execution" {      # Fargate pulls the image and writes logs with it
  name               = "gridcap-solve-execution"
  assume_role_policy = data.aws_iam_policy_document.assume["ecs-tasks.amazonaws.com"].json
}

resource "aws_iam_role_policy_attachment" "solve_execution" {
  role       = aws_iam_role.solve_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "solve_job" {            # what the solve itself may do: lesson 12.5.5's policy
  name               = "gridcap-solve-job"
  assume_role_policy = data.aws_iam_policy_document.assume["ecs-tasks.amazonaws.com"].json
}

resource "aws_iam_role_policy" "solve_job" {
  name   = "gridcap-solve-job"
  role   = aws_iam_role.solve_job.id
  policy = templatefile("${path.module}/solve-job-policy.json", { bucket_arn = aws_s3_bucket.runs.arn })
}

# ---- Batch on Fargate ------------------------------------------------------------------------

resource "aws_batch_compute_environment" "fargate" {
  name         = "gridcap-fargate"
  type         = "MANAGED"
  service_role = aws_iam_role.batch_service.arn

  compute_resources {
    type               = "FARGATE"
    max_vcpus          = 16
    subnets            = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  depends_on = [aws_iam_role_policy_attachment.batch_service]
}

resource "aws_batch_job_queue" "solves" {
  name     = "gridcap-solves"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.fargate.arn
  }
}

resource "aws_batch_job_definition" "solve" {
  name                  = "gridcap-solve"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.image
    command          = ["python", "-c", "import solve_worker; raise SystemExit(solve_worker.main())"]
    executionRoleArn = aws_iam_role.solve_execution.arn
    jobRoleArn       = aws_iam_role.solve_job.arn
    resourceRequirements = [
      { type = "VCPU", value = "2" },
      { type = "MEMORY", value = "8192" },
    ]
    environment = [
      { name = "RESULT_BUCKET", value = aws_s3_bucket.runs.bucket },
      { name = "PYTHON_CPU_COUNT", value = "2" },
    ]
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })

  retry_strategy {
    attempts = 2
  }

  timeout {
    attempt_duration_seconds = 3600
  }
}

# ---- The failure recorder and the state machine ------------------------------------------------

resource "aws_iam_role" "record_failure" {
  name               = "gridcap-record-failure"
  assume_role_policy = data.aws_iam_policy_document.assume["lambda.amazonaws.com"].json
}

resource "aws_iam_role_policy" "record_failure" {
  name = "gridcap-record-failure"
  role = aws_iam_role.record_failure.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = ["s3:PutObject"], Resource = ["${aws_s3_bucket.runs.arn}/results/*"] }]
  })
}

resource "aws_lambda_function" "record_failure" {
  function_name    = "gridcap-record-failure"
  role             = aws_iam_role.record_failure.arn
  filename         = "record_failure.zip"
  source_code_hash = filebase64sha256("record_failure.zip")
  handler          = "record_failure.handler"
  runtime          = "python3.13"
  timeout          = 30

  environment {
    variables = { RESULT_BUCKET = aws_s3_bucket.runs.bucket }
  }
}

resource "aws_iam_role" "solve_run" {
  name               = "gridcap-solve-run"
  assume_role_policy = data.aws_iam_policy_document.assume["states.amazonaws.com"].json
}

resource "aws_iam_role_policy" "solve_run" {   # the .sync pattern's policy, from the Step Functions docs
  name = "gridcap-solve-run"
  role = aws_iam_role.solve_run.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      { Effect = "Allow", Action = ["batch:SubmitJob", "batch:DescribeJobs", "batch:TerminateJob"], Resource = "*" },
      { Effect   = "Allow", Action = ["events:PutTargets", "events:PutRule", "events:DescribeRule"],
        Resource = "arn:aws:events:${var.region}:${data.aws_caller_identity.current.account_id}:rule/StepFunctionsGetEventsForBatchJobsRule" },
      { Effect = "Allow", Action = ["lambda:InvokeFunction"], Resource = aws_lambda_function.record_failure.arn },
    ]
  })
}

data "aws_caller_identity" "current" {}

resource "aws_sfn_state_machine" "solve_run" {
  name       = "gridcap-solve-run"
  role_arn   = aws_iam_role.solve_run.arn
  definition = file("${path.module}/../stepfunctions/solve-run.asl.json")
}
