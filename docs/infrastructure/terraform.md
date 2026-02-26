---
title: Terraform
description: Provision all required GCP and AWS cloud resources with a single terraform apply.
icon: simple/terraform
---

# Terraform Infrastructure

The `infra/` directory contains Terraform configuration that provisions all required cloud
resources for The Data Packet on Google Cloud Platform (GCS + TTS) and AWS (S3).

---

## Resources created

=== ":simple-googlecloud: Google Cloud"

    | Resource | Purpose |
    |---|---|
    | Cloud Text-to-Speech API | Long Audio Synthesis |
    | Cloud Storage API | GCS bucket access |
    | GCS Bucket | Intermediate audio storage (30-day lifecycle) |
    | Service Account `data-packet-service` | Minimal-permission app identity |
    | IAM `roles/cloudtts.user` | TTS operations |
    | IAM `roles/storage.admin` | GCS bucket management |
    | IAM `roles/storage.objectAdmin` | Object-level GCS access |

=== ":fontawesome-brands-aws: AWS"

    | Resource | Purpose |
    |---|---|
    | S3 Bucket `the-data-packet` | Podcast file hosting |
    | Public access config | Allows public read for distribution |

---

## Prerequisites

!!! info "Install these before running Terraform"

    - [Terraform ≥ 1.2](https://developer.hashicorp.com/terraform/downloads)
    - [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
    - [AWS CLI](https://aws.amazon.com/cli/)
    - A GCP project with billing enabled

---

## Step-by-step setup

**Step 1 — Authenticate**

```bash
# Google Cloud
gcloud auth login
gcloud auth application-default login
gcloud config set project your-gcp-project-id

# AWS
aws configure
```

**Step 2 — Configure variables**

```bash
cd infra/
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id        = "your-gcp-project-id"
region            = "us-central1"
audio_bucket_name = "your-unique-gcs-bucket-name"
```

**Step 3 — Deploy**

```bash
terraform init
terraform plan   # review what will be created
terraform apply
```

**Step 4 — Retrieve the service account key**

```bash
terraform output -raw service_account_key > key.b64
base64 -d key.b64 > service-account-key.json
chmod 600 service-account-key.json
```

!!! danger "Never commit this file"

    Add `service-account-key.json` to `.gitignore` immediately.

**Step 5 — Export environment variables**

```bash
export GCS_BUCKET_NAME="$(terraform output -raw gcs_bucket_name)"
export S3_BUCKET_NAME="$(terraform output -raw aws_s3_bucket_name)"
export GOOGLE_APPLICATION_CREDENTIALS="./service-account-key.json"
export ANTHROPIC_API_KEY="your-claude-api-key"
```

---

## Terraform outputs

| Output | Description |
|---|---|
| `gcs_bucket_name` | Value for `GCS_BUCKET_NAME` env var |
| `service_account_email` | Service account email |
| `service_account_key` | Base64-encoded key (sensitive) |
| `aws_s3_bucket_name` | Value for `S3_BUCKET_NAME` env var |

---

## Cost considerations

!!! tip "Costs are typically very low"

    - **GCS**: Pay-per-use storage. The 30-day lifecycle deletes old audio automatically.
    - **Google Cloud TTS Long Audio**: ~$16 per million characters. A typical episode is 5,000–10,000 characters.
    - **AWS S3**: Pay-per-use storage + GET requests (podcast downloads).

---

## Cleanup

```bash
terraform destroy
```

!!! warning

    Download any audio or episode files you want to keep from GCS and S3 before destroying.

---

## Useful commands

```bash
terraform show                              # current state
terraform state list                        # all resources
terraform output gcs_bucket_name            # single output
terraform state show google_storage_bucket.audio_bucket
terraform refresh                           # sync state with cloud
```

---

## Troubleshooting

| Error | Solution |
|---|---|
| `Project not found` | Check `project_id` in `terraform.tfvars` |
| `Permission denied` | Ensure your GCP account has `Owner` or `Editor` role |
| `Bucket name already exists` | GCS bucket names are globally unique — choose a different name |
| `API not enabled` | Terraform enables required APIs automatically on first `apply` |
