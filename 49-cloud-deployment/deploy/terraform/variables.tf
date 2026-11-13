# Read-along: never applied in this course. Values come from a terraform.tfvars file per environment.

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_name" {
  type        = string
  description = "The bucket for snapshots and results, e.g. gridcap-runs-example"
}

variable "image" {
  type        = string
  description = "The solver image with its immutable tag, as CI pushed it"
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}
