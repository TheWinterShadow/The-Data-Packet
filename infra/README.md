# Infrastructure Setup for The Data Packet

This directory contains Terraform configuration for provisioning the necessary cloud infrastructure for The Data Packet podcast generation system.

## Resources Created

### AWS Resources
- **S3 Bucket**: `the-data-packet` - For hosting generated podcast files and RSS feeds
- **Public Access Configuration**: Allows public read access for podcast distribution

### Google Cloud Resources
- **Text-to-Speech API**: Enabled for long audio synthesis
- **Cloud Storage API**: Enabled for audio file storage
- **GCS Bucket**: For storing synthesized audio files (with 30-day lifecycle)
- **Service Account**: `data-packet-service` with minimal required permissions
- **IAM Bindings**: 
  - `roles/cloudtts.user` - Text-to-Speech operations
  - `roles/storage.admin` - GCS bucket management
  - `roles/storage.objectAdmin` - Bucket-specific object operations

## Prerequisites

1. **Terraform**: Install Terraform >= 1.2
2. **Google Cloud CLI**: Install and authenticate
3. **AWS CLI**: Install and configure (for S3 resources)
4. **Google Cloud Project**: Create a GCP project with billing enabled

## Setup Instructions

### 1. Configure Google Cloud Authentication

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set your project (replace with your project ID)
gcloud config set project your-gcp-project-id
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI (for S3 resources)
aws configure
```

### 3. Configure Terraform Variables

```bash
# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
vim terraform.tfvars
```

Required variables in `terraform.tfvars`:
```hcl
project_id        = "your-gcp-project-id"
region            = "us-central1"
audio_bucket_name = "your-unique-bucket-name"
```

### 4. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Apply infrastructure changes
terraform apply
```

### 5. Retrieve Service Account Key

After successful deployment, get the service account key:

```bash
# Output the service account key (base64 encoded)
terraform output -raw service_account_key > service-account-key.json.b64

# Decode the key
base64 -d service-account-key.json.b64 > service-account-key.json

# Secure the key file
chmod 600 service-account-key.json
```

### 6. Configure Environment Variables

Set these environment variables for The Data Packet application:

```bash
# Required for Google Cloud TTS
export GCS_BUCKET_NAME="your-bucket-name-from-terraform-output"
export GOOGLE_APPLICATION_CREDENTIALS="./service-account-key.json"

# AWS S3 (existing)
export S3_BUCKET_NAME="the-data-packet"

# Other required variables
export ANTHROPIC_API_KEY="your-claude-api-key"
```

## Outputs

After deployment, Terraform provides these outputs:

- `gcs_bucket_name`: Name of the GCS bucket for audio files
- `service_account_email`: Email of the created service account
- `service_account_key`: Base64-encoded service account key (sensitive)
- `aws_s3_bucket_name`: Name of the AWS S3 bucket

## Security Considerations

1. **Service Account Key**: Store the service account key securely and never commit to version control
2. **Bucket Access**: The GCS bucket has restricted access via service account
3. **Lifecycle Policies**: Audio files are automatically deleted after 30 days
4. **Minimal Permissions**: Service account has only the permissions needed for operation

## Cost Management

- **GCS Bucket**: Pay-per-use storage and operations
- **Text-to-Speech API**: Pay per character processed
- **Lifecycle Policy**: Automatically deletes old files to minimize storage costs

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Project not found**: Ensure your GCP project ID is correct and you have access
2. **API not enabled**: Terraform will enable required APIs automatically
3. **Permission denied**: Ensure you have appropriate IAM permissions in your GCP project
4. **Bucket name conflicts**: GCS bucket names must be globally unique

### Useful Commands

```bash
# Check Terraform state
terraform show

# List all resources
terraform state list

# Get specific output
terraform output gcs_bucket_name

# Refresh state
terraform refresh
```