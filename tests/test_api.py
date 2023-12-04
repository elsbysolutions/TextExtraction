import pytest
from fastapi.testclient import TestClient
from ..api.app import app

client = TestClient(app)

def test_extract_text_endpoint():
    # Test a valid URL
    valid_url = "https://www.bbc.co.uk/news"  # Replace with a real URL
    response = client.post("/extract-text", json={"source_url": valid_url})
    assert response.status_code == 200
    data = response.json()
    assert "text" in data

    # Test an invalid URL (for example, a non-existent URL)
    invalid_url = "https://example-invalid-url.com"
    response = client.post("/extract-text", json={"source_url": invalid_url})
    assert response.status_code == 500  # You can adjust this based on your error handling
    data = response.json()
    assert "detail" in data