provider "aws" {
  region = "us-west-2"
}

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

