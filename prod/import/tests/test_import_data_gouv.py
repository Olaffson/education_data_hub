import pytest
from unittest.mock import patch, MagicMock
from src.import_data_gouv import check_files_exist, main
import os

def test_check_files_exist():
    with patch('src.import_data_gouv.get_blob_list') as mock_get_blobs:
        mock_get_blobs.return_value = [
            'data_gouv/ips_lycee.csv',
            'data_gouv/bac_par_academie.csv'
        ]
        assert check_files_exist() == False  # Car tous les fichiers ne sont pas présents
        
        mock_get_blobs.return_value = [
            'data_gouv/ips_lycee.csv',
            'data_gouv/bac_par_academie.csv',
            'data_gouv/ecoles_effectifs.csv',
            'data_gouv/ips_lycee_new.csv',
            'data_gouv/effectifs_tg.csv'
        ]
        assert check_files_exist() == True

@pytest.fixture
def mock_get_blobs():
    """Fixture pour mocker get_blob_list()"""
    with patch('src.import_data_gouv.get_blob_list') as mock_get_blob_list:
        yield mock_get_blob_list

@pytest.fixture
def mock_upload():
    """Fixture pour mocker upload_from_url()"""
    with patch('src.import_data_gouv.upload_from_url') as mock_upload:
        yield mock_upload

# ✅ Test `check_files_exist()` avec un blob vide
def test_check_files_exist_empty(mock_get_blobs):
    mock_get_blobs.return_value = []  # Aucun fichier existant
    assert check_files_exist() is False

# ✅ Test `check_files_exist()` lorsque tous les fichiers existent
def test_check_files_exist_all_files_present(mock_get_blobs):
    mock_get_blobs.return_value = [
        'data_gouv/ips_lycee.csv',
        'data_gouv/bac_par_academie.csv',
        'data_gouv/ecoles_effectifs.csv',
        'data_gouv/ips_lycee_new.csv',
        'data_gouv/effectifs_tg.csv'
    ]
    assert check_files_exist() is True

# ✅ Test `main()` lorsque tous les fichiers existent déjà
@patch("builtins.open", new_callable=MagicMock)
def test_main_no_action(mock_open, mock_get_blobs, mock_upload):
    mock_get_blobs.return_value = [
        'data_gouv/ips_lycee.csv',
        'data_gouv/bac_par_academie.csv',
        'data_gouv/ecoles_effectifs.csv',
        'data_gouv/ips_lycee_new.csv',
        'data_gouv/effectifs_tg.csv'
    ]

    main()
    
    mock_upload.assert_not_called()  # Aucun fichier ne doit être téléchargé
    mock_open.assert_called_once_with('skip_import', 'w')  # Vérifie que le fichier skip_import est écrit

# ✅ Test `main()` lorsque des fichiers sont absents et doivent être téléchargés
def test_main_download_missing_files(mock_get_blobs, mock_upload):
    mock_get_blobs.return_value = ['data_gouv/ips_lycee.csv']  # Seul un fichier existe

    main()

    # Vérifier que `upload_from_url()` a été appelé pour les fichiers manquants
    assert mock_upload.call_count == 5  # 5 fichiers doivent être téléchargés

# ✅ Test `main()` lorsque `upload_from_url()` lève une exception
def test_main_upload_error(mock_get_blobs, mock_upload):
    mock_get_blobs.return_value = []  # Aucun fichier existant
    mock_upload.side_effect = Exception("Erreur réseau")

    with pytest.raises(Exception, match="L'import s'est terminé avec 5 erreurs"):
        main()

# ✅ Test `check_files_exist()` avec une erreur dans `get_blob_list()`
def test_check_files_exist_get_blob_list_error(mock_get_blobs):
    mock_get_blobs.side_effect = Exception("Erreur de connexion à Azure")

    with pytest.raises(Exception, match="Erreur de connexion à Azure"):
        check_files_exist()
