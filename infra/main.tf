# ==============================================================================
# VARIABLES
# ==============================================================================
variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-central1"
}

variable "audio_bucket_name" {
  description = "Name for the Google Cloud Storage bucket for audio files"
  type        = string
  default     = "the-data-packet-audio"
}

# ==============================================================================
# PROVIDERS
# ==============================================================================
provider "aws" {
  region = "us-west-2"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ==============================================================================
# AWS RESOURCES (EXISTING)
# ==============================================================================
resource "aws_s3_bucket" "data_packet_bucket" {
  bucket = "the-data-packet"

  tags = {
    Name        = "The Data Packet Bucket"
    Environment = "Prod"
  }
}

resource "aws_s3_bucket_public_access_block" "data_packet_bucket_pab" {
  bucket = aws_s3_bucket.data_packet_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "data_packet_bucket_policy" {
  bucket = aws_s3_bucket.data_packet_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.data_packet_bucket.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.data_packet_bucket_pab]
}

# ==============================================================================
# GOOGLE CLOUD RESOURCES
# ==============================================================================

# Enable required Google Cloud APIs
resource "google_project_service" "texttospeech_api" {
  project = var.project_id
  service = "texttospeech.googleapis.com"
  
  disable_dependent_services = true
}

resource "google_project_service" "storage_api" {
  project = var.project_id
  service = "storage.googleapis.com"
  
  disable_dependent_services = true
}

# Google Cloud Storage bucket for audio synthesis output
resource "google_storage_bucket" "audio_bucket" {
  name     = var.audio_bucket_name
  location = var.region
  project  = var.project_id

  # Enable versioning for audio files
  versioning {
    enabled = true
  }

  # Lifecycle management to clean up old audio files
  lifecycle_rule {
    condition {
      age = 30  # Delete files older than 30 days
    }
    action {
      type = "Delete"
    }
  }

  # Enable uniform bucket-level access
  uniform_bucket_level_access = true

  labels = {
    environment = "production"
    purpose     = "audio-synthesis"
    managed_by  = "terraform"
  }
}

# Service account for The Data Packet application
resource "google_service_account" "data_packet_sa" {
  account_id   = "data-packet-service"
  display_name = "The Data Packet Service Account"
  description  = "Service account for The Data Packet podcast generation application"
  project      = var.project_id
}

# Generate service account key
resource "google_service_account_key" "data_packet_key" {
  service_account_id = google_service_account.data_packet_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Grant Text-to-Speech permissions to service account
resource "google_project_iam_member" "tts_user" {
  project = var.project_id
  role    = "roles/cloudtts.user"
  member  = "serviceAccount:${google_service_account.data_packet_sa.email}"
}

# Grant Storage permissions to service account  
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.data_packet_sa.email}"
}

# Grant specific bucket access
resource "google_storage_bucket_iam_member" "audio_bucket_admin" {
  bucket = google_storage_bucket.audio_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.data_packet_sa.email}"
}

# ==============================================================================
# OUTPUTS
# ==============================================================================

# AWS Outputs
output "aws_s3_bucket_name" {
  description = "Name of the AWS S3 bucket for podcast hosting"
  value       = aws_s3_bucket.data_packet_bucket.bucket
}

output "aws_s3_bucket_arn" {
  description = "ARN of the AWS S3 bucket"
  value       = aws_s3_bucket.data_packet_bucket.arn
}

# Google Cloud Outputs
output "gcs_bucket_name" {
  description = "Name of the Google Cloud Storage bucket for audio synthesis"
  value       = google_storage_bucket.audio_bucket.name
}

output "gcs_bucket_url" {
  description = "URL of the Google Cloud Storage bucket"
  value       = google_storage_bucket.audio_bucket.url
}

output "service_account_email" {
  description = "Email of the service account for The Data Packet"
  value       = google_service_account.data_packet_sa.email
}

output "service_account_key" {
  description = "Base64-encoded service account key (store securely)"
  value       = google_service_account_key.data_packet_key.private_key
  sensitive   = true
}

