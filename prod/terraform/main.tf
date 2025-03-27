provider "azurerm" {
  features {}
}

# Création du Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# Création du Storage Account (Data Lake Gen2)
resource "azurerm_storage_account" "datalake" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true # Data Lake Gen2 activé

  identity {
    type = "SystemAssigned"
  }
}

# Création des Containers (Blobs) pour le Data Lake
resource "azurerm_storage_container" "raw" {
  name                  = "raw"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "cleaned" {
  name                  = "cleaned"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "tables" {
  name                  = "tables"
  storage_account_id    = azurerm_storage_account.datalake.id
  container_access_type = "private"
}

# Création de la Data Factory
resource "azurerm_data_factory" "adf" {
  name                = var.data_factory_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "prod"
    managed_by  = "terraform"
  }
}

# Création du Linked Service vers Data Lake Gen2
resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "datalake" {
  name                 = "LinkedServiceDataLakeGen2"
  data_factory_id      = azurerm_data_factory.adf.id
  url                  = "https://${azurerm_storage_account.datalake.name}.dfs.core.windows.net"
  use_managed_identity = true
}

# Attribution du rôle Storage Blob Data Contributor à la Data Factory
resource "azurerm_role_assignment" "adf_storage_contributor" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.adf.identity[0].principal_id
}

# Serveur SQL Azure
resource "azurerm_mssql_server" "sql_server" {
  name                         = "sqlserver-${var.environment}"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password

  minimum_tls_version = "1.2"

  tags = {
    environment = var.environment
  }
}

# Base de données Azure SQL
resource "azurerm_mssql_database" "education_db" {
  name                 = "EducationData"
  server_id            = azurerm_mssql_server.sql_server.id
  sku_name             = "Basic"
  max_size_gb          = 2
  zone_redundant       = false
  collation            = "SQL_Latin1_General_CP1_CI_AS"
  storage_account_type = "Local"

  tags = {
    environment = var.environment
  }
}

# Pare-feu pour autoriser l'accès au SQL Server depuis tous les services Azure
resource "azurerm_mssql_firewall_rule" "allow_azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# # Dataset source pour les fichiers CSV de data_gouv
# resource "azurerm_data_factory_dataset_delimited_text" "data_gouv_csv" {
#   name                = "DataGouvCsvDataset"
#   data_factory_id     = azurerm_data_factory.adf.id
#   linked_service_name = azurerm_data_factory_linked_service_data_lake_storage_gen2.datalake.name

#   azure_blob_storage_location {
#     container = azurerm_storage_container.raw.name
#     path      = "data_gouv"
#     filename  = "*.csv"
#   }

#   column_delimiter    = ";"
#   row_delimiter       = "\n"
#   encoding            = "UTF-8"
#   quote_character     = "\""
#   escape_character    = "\\"
#   first_row_as_header = true
# }

# # Dataset destination pour les fichiers Parquet
# resource "azurerm_data_factory_dataset_parquet" "data_gouv_parquet" {
#   name                = "DataGouvParquetDataset"
#   data_factory_id     = azurerm_data_factory.adf.id
#   linked_service_name = azurerm_data_factory_linked_service_data_lake_storage_gen2.datalake.name

#   azure_blob_storage_location {
#     container = azurerm_storage_container.cleaned.name
#     path      = "data_gouv"
#   }

#   compression_codec = "snappy"
# }

# # Pipeline de conversion CSV vers Parquet
# resource "azurerm_data_factory_pipeline" "csv_to_parquet_pipeline" {
#   name            = "DataGouvCsvToParquet"
#   data_factory_id = azurerm_data_factory.adf.id

#   activities_json = jsonencode([
#     {
#       name = "CsvToParquet",
#       type = "Copy",
#       inputs = [{
#         referenceName = azurerm_data_factory_dataset_delimited_text.data_gouv_csv.name,
#         type          = "DatasetReference"
#       }],
#       outputs = [{
#         referenceName = azurerm_data_factory_dataset_parquet.data_gouv_parquet.name,
#         type          = "DatasetReference"
#       }],
#       typeProperties = {
#         source = {
#           type = "DelimitedTextSource",
#           storeSettings = {
#             type             = "AzureBlobFSReadSettings",
#             recursive        = true,
#             wildcardFileName = "*.csv"
#           }
#         },
#         sink = {
#           type = "ParquetSink",
#           storeSettings = {
#             type = "AzureBlobFSWriteSettings"
#           },
#           formatSettings = {
#             type = "ParquetWriteSettings"
#           }
#         }
#       }
#     }
#   ])
# }

# # Trigger pour surveiller les nouveaux fichiers CSV
# resource "azurerm_data_factory_trigger_blob_event" "trigger_data_gouv" {
#   name               = "TriggerDataGouv"
#   data_factory_id    = azurerm_data_factory.adf.id
#   storage_account_id = azurerm_storage_account.datalake.id

#   events = ["Microsoft.Storage.BlobCreated"]

#   scope = "/subscriptions/${var.subscription_id}/resourceGroups/${azurerm_resource_group.rg.name}/providers/Microsoft.Storage/storageAccounts/${azurerm_storage_account.datalake.name}/blobServices/default/containers/${azurerm_storage_container.raw.name}/blobs/data_gouv"

#   pipeline {
#     name = azurerm_data_factory_pipeline.csv_to_parquet_pipeline.name
#   }
# }

