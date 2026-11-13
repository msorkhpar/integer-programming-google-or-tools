# Read-along: what the API's configuration reads after an apply (terraform output -json).

output "bucket" {
  value = aws_s3_bucket.runs.bucket
}

output "job_queue" {
  value = aws_batch_job_queue.solves.name
}

output "job_definition" {
  value = aws_batch_job_definition.solve.name
}

output "state_machine_arn" {
  value = aws_sfn_state_machine.solve_run.arn
}
