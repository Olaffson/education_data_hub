from unittest.mock import MagicMock, patch

import pytest

from src.import_data_opendatasoft import check_files_exist, fetch_json_data, main, upload_json_to_azure


def test_fetch_json_data():
    with patch("src.import_data_opendatasoft.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"results": [{"id": 1}]}
        results = fetch_json_data("http://test.com")
        assert results == [{"id": 1}]


def test_check_files_exist():
    with patch("src.import_data_opendatasoft.get_blob_list") as mock_get_blobs:
        mock_get_blobs.return_value = ["opendatasoft/lycees-donnees-generales-combine.json"]
        assert check_files_exist() == True

        mock_get_blobs.return_value = []
        assert check_files_exist() == False


@pytest.fixture
def mock_get_blobs():
    """
    Fixture pour simuler la récupération des fichiers dans Azure.
    """
    with patch("src.import_data_opendatasoft.get_blob_list") as mock_get_blob_list:
        yield mock_get_blob_list


@pytest.fixture
def mock_upload_to_azure():
    """
    Fixture pour éviter d'uploader réellement des fichiers pendant les tests.
    """
    with patch("src.import_data_opendatasoft.upload_json_to_azure") as mock_upload:
        yield mock_upload


@pytest.fixture
def mock_requests_get():
    """
    Fixture pour mocker requests.get et éviter des appels réels à l'API.
    """
    with patch("src.import_data_opendatasoft.requests.get") as mock_get:
        yield mock_get


def test_fetch_json_data_success(mock_requests_get):
    """
    Vérifie que fetch_json_data récupère correctement les données JSON.
    """
    mock_requests_get.return_value.json.return_value = {"results": [{"id": 1}, {"id": 2}]}
    results = fetch_json_data("http://test.com")
    assert results == [{"id": 1}, {"id": 2}]
    mock_requests_get.assert_called_once_with("http://test.com")


def test_fetch_json_data_error(mock_requests_get):
    """
    Vérifie que fetch_json_data gère les erreurs d'API.
    """
    mock_requests_get.side_effect = Exception("Erreur de requête")
    with pytest.raises(Exception, match="Erreur de requête"):
        fetch_json_data("http://test.com")


def test_check_files_exist_true(mock_get_blobs):
    """
    Vérifie que check_files_exist retourne True si le fichier existe déjà.
    """
    mock_get_blobs.return_value = ["opendatasoft/lycees-donnees-generales-combine.json"]
    assert check_files_exist() is True


def test_check_files_exist_false(mock_get_blobs):
    """
    Vérifie que check_files_exist retourne False si le fichier n'existe pas.
    """
    mock_get_blobs.return_value = []
    assert check_files_exist() is False
