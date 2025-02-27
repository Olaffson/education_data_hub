import pytest
from unittest.mock import patch, MagicMock
from azure.core.exceptions import AzureError
from src.azure_upload import upload_json_to_azure, upload_from_url, check_blob_exists, get_blob_list

@pytest.fixture
def mock_container_client():
    return MagicMock()

@pytest.fixture
def mock_blob_client():
    return MagicMock()

@patch('src.azure_upload.container_client')
def test_upload_json_to_azure(mock_container_client):
    # Configurer le mock pour le blob client
    mock_blob_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client
    
    # Exécuter la fonction
    test_data = {"test": "data"}
    upload_json_to_azure(test_data, "test_folder", "test.json")
    
    # Vérifier les appels
    mock_container_client.get_blob_client.assert_called_once_with("test_folder/test.json")
    mock_blob_client.upload_blob.assert_called_once()
    # Vérifier que le contenu JSON est correct
    args, kwargs = mock_blob_client.upload_blob.call_args
    assert kwargs['overwrite'] is True
    assert isinstance(args[0], bytes)  # Vérifie que le contenu est encodé en bytes

@patch('src.azure_upload.container_client')
def test_upload_from_url(mock_container_client):
    # Configurer le mock pour le blob client
    mock_blob_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client
    
    # Mock la réponse requests
    with patch('src.azure_upload.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.raw = "test_content"
        mock_get.return_value = mock_response
        mock_response.raise_for_status = MagicMock()
        
        # Exécuter la fonction
        upload_from_url("http://test.com", "test_folder", "test.file")
        
        # Vérifier les appels
        mock_get.assert_called_once_with("http://test.com", stream=True)
        mock_container_client.get_blob_client.assert_called_once_with("test_folder/test.file")
        mock_blob_client.upload_blob.assert_called_once_with("test_content", overwrite=True)

@patch('src.azure_upload.container_client')
def test_check_blob_exists(mock_container_client):
    # Configurer le mock pour le blob client
    mock_blob_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client
    mock_blob_client.exists.return_value = True
    
    # Exécuter et vérifier
    result = check_blob_exists("test_folder", "test.file")
    assert result is True
    mock_container_client.get_blob_client.assert_called_once_with("test_folder/test.file")
    mock_blob_client.exists.assert_called_once()

@patch('src.azure_upload.container_client')
def test_get_blob_list(mock_container_client):
    # Configurer le mock pour list_blobs
    mock_blob1 = MagicMock()
    mock_blob1.name = "test_folder/file1.txt"
    mock_blob2 = MagicMock()
    mock_blob2.name = "test_folder/file2.txt"
    mock_container_client.list_blobs.return_value = [mock_blob1, mock_blob2]
    
    # Exécuter et vérifier
    result = get_blob_list("test_folder")
    assert result == ["test_folder/file1.txt", "test_folder/file2.txt"]
    mock_container_client.list_blobs.assert_called_once_with(name_starts_with="test_folder")

# ✅ Test de l'upload JSON avec un fichier vide
@patch('src.azure_upload.container_client')
def test_upload_json_to_azure_empty_json(mock_container_client):
    mock_blob_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client

    empty_json = {}
    upload_json_to_azure(empty_json, "test_folder", "empty.json")

    mock_blob_client.upload_blob.assert_called_once()
    args, kwargs = mock_blob_client.upload_blob.call_args
    assert kwargs['overwrite'] is True
    assert isinstance(args[0], bytes)  # Vérifier que c'est bien encodé en bytes

# ✅ Test de l'upload JSON avec une erreur Azure
@patch('src.azure_upload.container_client')
def test_upload_json_to_azure_azure_error(mock_container_client):
    mock_blob_client = MagicMock()
    mock_blob_client.upload_blob.side_effect = AzureError("Erreur Azure")
    mock_container_client.get_blob_client.return_value = mock_blob_client

    with pytest.raises(AzureError, match="Erreur Azure"):
        upload_json_to_azure({"test": "data"}, "test_folder", "error.json")

# ✅ Test de l'upload depuis URL avec une URL invalide
@patch('src.azure_upload.container_client')
@patch('src.azure_upload.requests.get')
def test_upload_from_url_invalid_url(mock_requests_get, mock_container_client):
    mock_requests_get.side_effect = Exception("Invalid URL")

    with pytest.raises(Exception, match="Invalid URL"):
        upload_from_url("http://invalid-url.com", "test_folder", "invalid.file")

# ✅ Test de l'upload depuis URL avec une erreur Azure
@patch('src.azure_upload.container_client')
@patch('src.azure_upload.requests.get')
def test_upload_from_url_azure_error(mock_requests_get, mock_container_client):
    mock_blob_client = MagicMock()
    mock_blob_client.upload_blob.side_effect = AzureError("Azure Storage Error")
    mock_container_client.get_blob_client.return_value = mock_blob_client

    mock_requests_get.return_value.raw = b"test data"
    mock_requests_get.return_value.raise_for_status = MagicMock()

    with pytest.raises(AzureError, match="Azure Storage Error"):
        upload_from_url("http://valid-url.com", "test_folder", "test.file")

# ✅ Test `check_blob_exists()` quand le blob n'existe pas
@patch('src.azure_upload.container_client')
def test_check_blob_exists_not_found(mock_container_client):
    mock_blob_client = MagicMock()
    mock_blob_client.exists.return_value = False
    mock_container_client.get_blob_client.return_value = mock_blob_client

    assert check_blob_exists("test_folder", "missing.file") is False
    mock_blob_client.exists.assert_called_once()

# ✅ Test `get_blob_list()` avec une liste vide
@patch('src.azure_upload.container_client')
def test_get_blob_list_empty(mock_container_client):
    mock_container_client.list_blobs.return_value = []

    result = get_blob_list("empty_folder")
    assert result == []
    mock_container_client.list_blobs.assert_called_once_with(name_starts_with="empty_folder")
