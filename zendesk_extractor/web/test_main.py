import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from zendesk_extractor.web.main import app
import os

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def create_dummy_files():
    os.makedirs("output/json", exist_ok=True)
    os.makedirs("output/xml", exist_ok=True)
    with open("output/json/test.json", "w") as f:
        f.write("{}")
    with open("output/xml/test.xml", "w") as f:
        f.write("<test/>")
    yield
    os.remove("output/json/test.json")
    os.remove("output/xml/test.xml")

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

@patch('zendesk_extractor.web.main.run_extraction')
def test_extract(mock_run_extraction):
    response = client.post("/extract")
    assert response.status_code == 200
    assert response.json() == {"message": "Extraction process started."}
    mock_run_extraction.assert_called_once()

def test_list_files():
    response = client.get("/files")
    assert response.status_code == 200
    assert "json_files" in response.json()
    assert "xml_files" in response.json()

def test_get_json_file():
    response = client.get("/files/json/test.json")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/json'

def test_get_xml_file():
    response = client.get("/files/xml/test.xml")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/xml'
