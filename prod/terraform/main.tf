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

# Dataset source pour les fichiers bruts
resource "azurerm_data_factory_dataset_delimited_text" "raw_dataset" {
  name                = "RawDataset"
  data_factory_id     = azurerm_data_factory.adf.id
  linked_service_name = azurerm_data_factory_linked_service_data_lake_storage_gen2.datalake.name

  azure_blob_storage_location {
    container = azurerm_storage_container.raw.name
    path      = "data_gouv"
    filename  = "*.csv"
  }

  column_delimiter    = ";"
  row_delimiter       = "NEW_LINE"
  encoding            = "UTF-8"
  quote_character     = "\""
  escape_character    = "\\"
  first_row_as_header = true
}

# Dataset destination pour les fichiers nettoyés
resource "azurerm_data_factory_dataset_delimited_text" "cleaned_dataset" {
  name                = "CleanedDataset"
  data_factory_id     = azurerm_data_factory.adf.id
  linked_service_name = azurerm_data_factory_linked_service_data_lake_storage_gen2.datalake.name

  azure_blob_storage_location {
    container = azurerm_storage_container.cleaned.name
    path      = "data_gouv"
    filename  = "cleaned_{timestamp}.csv"
  }

  column_delimiter    = ";"
  row_delimiter       = "NEW_LINE"
  encoding            = "UTF-8"
  quote_character     = "\""
  escape_character    = "\\"
  first_row_as_header = true
}

# Pipeline de nettoyage des données
resource "azurerm_data_factory_pipeline" "cleaning_pipeline" {
  name            = "DataCleaningPipeline"
  data_factory_id = azurerm_data_factory.adf.id

  activities_json = jsonencode([
    {
      name = "CopyData",
      type = "Copy",
      inputs = [{
        referenceName = azurerm_data_factory_dataset_delimited_text.raw_dataset.name,
        type          = "DatasetReference"
      }],
      outputs = [{
        referenceName = azurerm_data_factory_dataset_delimited_text.cleaned_dataset.name,
        type          = "DatasetReference"
      }],
      typeProperties = {
        source = {
          type = "DelimitedTextSource",
          storeSettings = {
            type      = "AzureBlobFSReadSettings",
            recursive = true
          }
        },
        sink = {
          type = "DelimitedTextSink",
          storeSettings = {
            type = "AzureBlobFSWriteSettings"
          }
        }
      }
    }
  ])
}

# Attribution du rôle Storage Blob Data Contributor à la Data Factory
resource "azurerm_role_assignment" "adf_storage_contributor" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.adf.identity[0].principal_id
}
