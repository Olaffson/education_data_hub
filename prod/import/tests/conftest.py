import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_blob_service_client():
    mock_client = MagicMock()
    return mock_client

@pytest.fixture
def mock_container_client():
    mock_client = MagicMock()
    return mock_client

@pytest.fixture
def mock_blob_client():
    mock_client = MagicMock()
    return mock_client