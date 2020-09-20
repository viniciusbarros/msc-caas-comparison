variable region {
    description = "AWS Region to be used"
    default = "us-east-1"
}

variable access_key {
    description = "Access key to grant access to resources"
    default = ""
}

variable secret_key {
    description = "Access secret key to grant access to resources"
    default = ""
}

variable token {
    description = "token for MFA"
    default = ""
}

variable cpu {
    description = "Amount of CPU to be used"
    default = 512
}

variable memory  {
    description = "Amount of RAM to be used"
    default = 1024
}

variable docker_image {
    description = "Docker image to be deployed"
    default = "viniciusbarros/msc-performance-web-app:latest"
}