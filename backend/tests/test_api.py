import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.session import get_session
from app.domain.enums import ApplicationStatus, Country, CustomerType
from app.main import app


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def test_create_application_returns_first_step_and_progress(client):
    response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["country"] == "sweden"
    assert body["customer_type"] == "private"
    assert body["status"] == ApplicationStatus.IN_PROGRESS.value
    assert body["current_step"] == "personal_info"
    assert body["progress"] == {"completed": 0, "total": 6}


async def test_get_application_returns_404_for_unknown_id(client):
    response = await client.get(
        "/api/v1/applications/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


async def test_get_application_returns_full_step_list(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "poland", "customer_type": "business"}
    )
    application_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/applications/{application_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] is None
    assert len(body["steps"]) == 7
    assert all(step["status"] == "pending" for step in body["steps"])


async def test_get_current_step_matches_first_flow_step(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "spain", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/applications/{application_id}/steps/current")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "personal_info"
    assert body["position"] == 1
    assert body["total_steps"] == 6
    assert body["status"] == "pending"
