version: '3.8'

# Infrastructure as Code - Infrastructure definitions for OmniSight

# This directory contains Infrastructure as Code templates for deploying OmniSight:
# - docker-compose.yml: Local development stack
# - Kubernetes manifests: Production deployment
# - Terraform: Cloud infrastructure (AWS, GCP, Azure)
# - Helm charts: Package management

# For production deployments, use:
# - helm install omnisight ./helm -f helm-values.yaml
# - kubectl apply -f k8s/
# - terraform apply -f terraform/main.tf
