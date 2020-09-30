variable "project" {
  description = "Project Name"
  default     = "vmbarross"
}

variable "region" {
  description = "Region to be used"
  default     = "us-east4"
}

variable "zone" {
  description = "Zone within region to deploy"
  default     = "us-east4-a"
}

variable cpu {
    description = "Amount of CPU to be used - k8s Style"
    default = "1000m"
}

variable memory  {
    description = "Amount of RAM to be used - k8s Style"
    default = "256Mi"
}


