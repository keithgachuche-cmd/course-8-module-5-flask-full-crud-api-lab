from app import app, events, Event
import pytest

@pytest.fixture(autouse=True)
def reset_data():
    # Reset the in-memory "database" before each test
    events.clear()
    events.append(Event(1, "Tech Meetup"))
    events.append(Event(2, "Python Workshop"))

def test_create_event():
    client = app.test_client()
    response = client.post("/events", json={"title": "Hackathon"})
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data and data["title"] == "Hackathon"

def test_update_event():
    client = app.test_client()
    response = client.patch("/events/1", json={"title": "Hackathon 2025"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Hackathon 2025"

def test_update_event_not_found():
    client = app.test_client()
    response = client.patch("/events/99", json={"title": "Ghost Event"})
    assert response.status_code == 404

def test_delete_event():
    client = app.test_client()
    response = client.delete("/events/2")
    assert response.status_code == 204

def test_delete_event_not_found():
    client = app.test_client()
    response = client.delete("/events/99")
    assert response.status_code == 404

def test_home():
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert "message" in response.get_json()

def test_get_events():
    response = app.test_client().get("/events")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list) and len(data) == 2

def test_create_event_missing_title():
    client = app.test_client()
    assert client.post("/events", json={}).status_code == 400
    assert client.post("/events").status_code == 400

def test_update_event_missing_title():
    response = app.test_client().patch("/events/1", json={})
    assert response.status_code == 400

def test_ids_unique_after_delete():
    client = app.test_client()
    client.delete("/events/2")
    new = client.post("/events", json={"title": "New"}).get_json()
    assert new["id"] == 2 or new["id"] > 1
    assert len({e["id"] for e in client.get("/events").get_json()}) == 2