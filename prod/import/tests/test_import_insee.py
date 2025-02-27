from unittest.mock import MagicMock, patch

import pytest

from src.import_insee import check_files_exist, main


def test_check_files_exist():
    with patch("src.import_insee.get_blob_list") as mock_get_blobs:
        mock_get_blobs.return_value = ["insee/financement.xlsx"]
        assert check_files_exist() == True

        mock_get_blobs.return_value = []
        assert check_files_exist() == False


@pytest.mark.integration
def test_main_skip_if_files_exist():
    with patch("src.import_insee.check_files_exist") as mock_check:
        mock_check.return_value = True
        main()
        # Vérifier que le fichier skip_import a été créé
