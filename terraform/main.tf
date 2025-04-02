# Define the provider and authenticate with the service account
provider "google" {
  credentials = file("../credentials.json")
  project     = var.project_id
  region      = var.region
}

# Create a Compute Engine Virtual Machine (VM)
resource "google_compute_instance" "vm_instance" {
  name         = "us-natality-vm"
  machine_type = "e2-standard-4"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 30
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
}

# Create a Google Cloud Storage Bucket
resource "google_storage_bucket" "bucket" {
  name          = "us-natality-bucket"
  location      = var.region
  storage_class = "STANDARD"
  force_destroy = true
}

# Create a BigQuery Dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = "us_natality_dataset"
  project                    = var.project_id
  location                   = var.region
  delete_contents_on_destroy = true
}
