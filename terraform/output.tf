output "app_url" {
  description = "Public application URL"
  value       = "http://${aws_lb.main.dns_name}"
}