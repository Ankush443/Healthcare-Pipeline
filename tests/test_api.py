from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Healthcare Data API is running"


def test_get_records():
    response = client.get("/records?page=1&page_size=10")

    assert response.status_code == 200

    data = response.json()

    assert "records" in data
    assert "total" in data
    assert "total_pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_get_records_pagination():
    response = client.get("/records?page=1&page_size=5")

    assert response.status_code == 200

    data = response.json()

    assert len(data["records"]) <= 5


def test_invalid_page():
    response = client.get("/records?page=0")

    assert response.status_code == 422


def test_invalid_page_size():
    response = client.get("/records?page=1&page_size=101")

    assert response.status_code == 422


def test_get_single_record():
    response = client.get("/records/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1


def test_record_not_found():
    response = client.get("/records/999999")

    assert response.status_code == 404


def test_get_stats():
    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert "total_records" in data
    assert "average_patient_age" in data
    assert "serious_distribution" in data
    assert "top_countries" in data
    assert "top_reactions" in data

    assert data["total_records"] > 0