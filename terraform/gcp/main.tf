terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  version = "3.39.0"

  credentials = file("key.json")

  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_cloud_run_service" "default" {
  name     = "msc-performance-web-app-tf"
  location = var.region

  traffic {
    percent         = 100
    latest_revision = true
  }

  template {
    spec {
      containers {
        image = "gcr.io/vmbarross/msc-performance-web-app"
        ports {
          container_port = 80
        }

        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }
      }
      container_concurrency = 0
      timeout_seconds = 900
    }
  }
}
# Allowing unauthenticated requests
data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}


resource "google_cloud_run_service_iam_policy" "noauth" {
  location    = google_cloud_run_service.default.location
  project     = google_cloud_run_service.default.project
  service     = google_cloud_run_service.default.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

output "service_url" {
  value       = google_cloud_run_service.default.status
  description = "URL to access the app"
}