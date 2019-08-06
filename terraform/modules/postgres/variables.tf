variable "hostRootPath" {
  type = "string"
}

variable "workspace" {
  type = "string"
  default = "dev"
}

variable "postgres" {
  type = "map"
  default = {
    username = "pguser"
  }
}

variable "images" {
  type = "map"
  default = {
    postgres = ":10.9"
  }
}

variable "network" {
  type = "string"
}

variable "externalPort" {
  type = "string"
  default = "5432"
}

variable "upgrade_support_for_gssapi_authentication" {
  type = "string"
  default = "false"
}

variable "krb_realm" {
  type = "string"
  default = ""
}
