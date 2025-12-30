terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.10.0"
    }
  }

  required_version = ">= 1.2"
}