import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import RESUME_COOKIE_NAME
from app.db.session import get_session
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


async def test_create_application_sets_resume_cookie(client):
    response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    assert RESUME_COOKIE_NAME in response.cookies


async def test_resume_returns_the_application_from_the_cookie(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "poland", "customer_type": "business"}
    )
    application_id = create_response.json()["id"]

    resume_response = await client.get("/api/v1/resume")

    assert resume_response.status_code == 200
    body = resume_response.json()
    assert body["application_id"] == application_id
    assert body["current_step"] == "organisation_info"
    assert body["status"] == "in_progress"


async def test_resume_returns_404_without_a_cookie(client):
    response = await client.get("/api/v1/resume")
    assert response.status_code == 404


async def test_resume_returns_404_for_an_unknown_token(client):
    client.cookies.set(RESUME_COOKIE_NAME, "not-a-real-token")
    response = await client.get("/api/v1/resume")
    assert response.status_code == 404


async def test_clear_resume_cookie_makes_resume_404_again(client):
    await client.post("/api/v1/applications", json={"country": "spain", "customer_type": "private"})
    assert (await client.get("/api/v1/resume")).status_code == 200

    clear_response = await client.post("/api/v1/resume/clear")
    assert clear_response.status_code == 204

    assert (await client.get("/api/v1/resume")).status_code == 404
