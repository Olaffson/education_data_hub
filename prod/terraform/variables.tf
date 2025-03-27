variable "resource_group_name" {
  description = "Nom du Resource Group"
  type        = string
  default     = "RG-OKOTWICA-Prod"
}

variable "location" {
  description = "Région Azure"
  type        = string
  default     = "francecentral"
}

variable "storage_account_name" {
  description = "Nom du Storage Account"
  type        = string
  default     = "sadatalakeokotwicaprod"
}

variable "data_factory_name" {
  description = "Nom de la Data Factory"
  type        = string
  default     = "adf-okotwica-prod"
}

variable "sql_admin_username" {
  description = "Nom d'utilisateur administrateur SQL"
  type        = string
}

variable "sql_admin_password" {
  description = "Mot de passe administrateur SQL"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environnement (ex: dev, prod)"
  type        = string
  default     = "prod"
}
