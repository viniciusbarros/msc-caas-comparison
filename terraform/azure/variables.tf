variable "subscription" {
  description = "Azure Subscription ID"
  default     = ""
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  default     = ""
}

variable "resource_group" {
  description = "Azure Tenant ID"
  default     = "msc-caas-resource-group"
}

variable "dns" {
  description = "The dns to be created"
  default     = "msc-caas"
}

variable "location" {
  description = "The Azure location where all resources in this example should be created"
  default     = "East US"
}

variable docker_image {
    description = "Docker image to be deployed"
    default = "viniciusbarros/msc-performance-web-app:latest"
}

variable cpu {
    description = "Amount of CPU to be used"
    default = "1"
}

variable memory  {
    description = "Amount of RAM to be used"
    default = "0.5"
}
