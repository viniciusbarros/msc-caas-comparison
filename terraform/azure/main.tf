
provider "azurerm" {
  subscription_id = var.subscription
  tenant_id       = var.tenant_id
  features {}
  version = "2.28.0"
}

resource "azurerm_resource_group" "example" {
  name     = var.resource_group
  location = var.location
}

resource "azurerm_container_group" "example" {
  name                = "msc-caas-container"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  ip_address_type     = "public"
  os_type             = "linux"
  dns_name_label      = var.dns

  container {
    name   = "msc-caas-comparison-container"
    image  = var.docker_image
    cpu    = var.cpu
    memory = var.memory
    ports {
      port     = 80
      protocol = "TCP"
    }
  }

  tags = {
    environment = "testing"
  }
}

output "service_url" {
  value       = azurerm_container_group.example.fqdn
  description = "URL to access the app"
}