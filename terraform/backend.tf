terraform {
  backend "s3" {
    bucket = "url-shortener-terraform-state-s3"
    key    = "global/s3/terraform.tfstate"
    region = "us-east-2"
  }
}