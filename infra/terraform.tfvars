# ==============================================================================
# TERRAFORM VARIABLES
# ==============================================================================
# This file contains variable definitions for The Data Packet infrastructure.
# Set these values in terraform.tfvars or pass via command line.

# Google Cloud Project Configuration
project_id = "gen-lang-client-0429374219"
region     = "us-central1"

# Storage Configuration
audio_bucket_name = "the-data-packet-audio"

# Optional: Override default settings
# region = "us-west1"  # Alternative region closer to your location