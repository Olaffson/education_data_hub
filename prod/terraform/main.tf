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

# -----------------------------
# 1. DATASETS SOURCES
# -----------------------------

# CSV Dataset - raw/data_gouv/*.csv
resource "azurerm_data_factory_dataset_delimited_text" "csv_dataset" {
  name                = "CsvDataset"
  data_factory_id     = azurerm_data_factory.adf.id
  linked_service_name = azurerm_data_factory_linked_service_data_lake_storage_gen2.datalake.name

  azure_blob_storage_location {
    container = azurerm_storage_container.raw.name
    path      = "data_gouv"
    filename  = "*.csv"
  }

  column_delimiter    = ";"
  row_delimiter       = "\n"
  encoding            = "UTF-8"
  quote_character     = "\""
  escape_character    = "\\"
  first_row_as_header = true
}

# -----------------------------
# 2. DATASET PARQUET DESTINATION
# -----------------------------

resource "azurerm_data_factory_dataset_parquet" "parquet_output" {
  name                = "ParquetOutput"
  data_factory_id     = azurerm_data_factory.adf.id
  linked_service_name = azurerm_data_factory_linked_service_data_lake_storage_gen2.datalake.name

  azure_blob_storage_location {
    container = azurerm_storage_container.cleaned.name
    path      = "@{pipeline().parameters.outputPath}"
    filename  = "@{pipeline().parameters.outputName}"
  }
}

# -----------------------------
# 3. PIPELINE with 3 activities
# -----------------------------

resource "azurerm_data_factory_pipeline" "universal_parquet_pipeline" {
  name            = "UniversalConvertToParquet"
  data_factory_id = azurerm_data_factory.adf.id

  parameters = {
    outputPath = "default"
    outputName = "default.parquet"
  }

  activities_json = jsonencode([
    {
      name    = "CopyCsv",
      type    = "Copy",
      inputs  = [{ referenceName = azurerm_data_factory_dataset_delimited_text.csv_dataset.name, type = "DatasetReference" }],
      outputs = [{ referenceName = azurerm_data_factory_dataset_parquet.parquet_output.name, type = "DatasetReference" }],
      typeProperties = {
        source = {
          type          = "DelimitedTextSource",
          storeSettings = { type = "AzureBlobFSReadSettings", recursive = true }
        },
        sink = {
          type          = "ParquetSink",
          storeSettings = { type = "AzureBlobFSWriteSettings" }
        }
      }
    }
  ])
}

# -----------------------------
# 4. EVENT TRIGGER AUTOMATIQUE
# -----------------------------

resource "azurerm_data_factory_trigger_blob_event" "trigger_data_gouv" {
  name               = "TriggerDataGouv"
  data_factory_id    = azurerm_data_factory.adf.id
  storage_account_id = azurerm_storage_account.datalake.id

  events = ["Microsoft.Storage.BlobCreated"]

  # IMPORTANT : Ne pas mettre "raw/" ni "blobs/" ni "/" au début
  blob_path_begins_with = "data_gouv"

  pipeline {
    name = azurerm_data_factory_pipeline.universal_parquet_pipeline.name
    parameters = {
      outputPath = "@{triggerBody().folderPath}"
      outputName = "@{replace(triggerBody().fileName, '\\.[^.]+$', '.parquet')}"
    }
  }
}

# Attribution du rôle Storage Blob Data Contributor à la Data Factory
resource "azurerm_role_assignment" "adf_storage_contributor" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.adf.identity[0].principal_id
}

