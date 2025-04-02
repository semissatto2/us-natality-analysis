# Define variables for project, region, zone, and service account email

variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "us-natality-455214" # TODO: insert projet id here
}

variable "region" {
  description = "The region where resources will be created"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The zone where the VM instance will be created"
  type        = string
  default     = "us-central1-a"
}

variable "service_account_email" {
  description = "The email of the service account"
  type        = string
  default     = "us-natality-sa@us-natality-455214.iam.gserviceaccount.com" # TODO: insert SA here
}
