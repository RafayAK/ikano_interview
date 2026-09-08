import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.session import get_session
from app.domain.enums import ApplicationStatus, Decision
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


async def _complete_sweden_private_steps(client, application_id, identifier: str):
    await client.put(
        f"/api/v1/applications/{application_id}/steps/personal_info",
        json={"personal_identity_number": identifier},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/address_info",
        json={
            "email": "a@example.com",
            "phone": "+46701234567",
            "address_line1": "Main st 1",
            "city": "Stockholm",
            "postal_code": "11122",
        },
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/consent",
        json={"consent_given": True, "pep_sanctions_declaration": True, "tax_residency": "SE"},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/employment_income",
        json={"employment_status": "employed", "monthly_income": 30000, "household_size": 2},
    )
    await client.put(f"/api/v1/applications/{application_id}/steps/credit_decision", json={})
    return await client.put(
        f"/api/v1/applications/{application_id}/steps/review_submit",
        json={"accept_terms": True},
    )


async def test_sweden_private_clean_identifier_is_approved_on_submit(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    last_step_response = await _complete_sweden_private_steps(client, application_id, "199001011234")
    assert last_step_response.status_code == 200
    assert last_step_response.json()["current_step"] is None

    submit_response = await client.put(f"/api/v1/applications/{application_id}/submit")
    assert submit_response.status_code == 200
    body = submit_response.json()
    assert body["status"] == ApplicationStatus.APPROVED.value
    assert body["decision"] == Decision.APPROVED.value

    audit_response = await client.get(f"/api/v1/applications/{application_id}/audit-events")
    event_types = [event["event_type"] for event in audit_response.json()]
    assert "application_created" in event_types
    assert event_types.count("step_completed") == 6
    assert "decision_made" in event_types
    assert "application_submitted" in event_types


async def test_sweden_private_identifier_ending_999_is_rejected_on_submit(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    await _complete_sweden_private_steps(client, application_id, "199001011999")

    submit_response = await client.put(f"/api/v1/applications/{application_id}/submit")
    assert submit_response.status_code == 200
    body = submit_response.json()
    assert body["status"] == ApplicationStatus.REJECTED.value
    assert "identity_not_verified" in body["decision_reasons"]


async def test_sweden_private_identifier_ending_000_is_manual_review_on_submit(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    await _complete_sweden_private_steps(client, application_id, "199001011000")

    submit_response = await client.put(f"/api/v1/applications/{application_id}/submit")
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == ApplicationStatus.MANUAL_REVIEW.value


async def test_completing_a_non_current_step_returns_409(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/applications/{application_id}/steps/review_submit",
        json={"accept_terms": True},
    )
    assert response.status_code == 409


async def test_submitting_before_all_steps_complete_returns_409(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    response = await client.put(f"/api/v1/applications/{application_id}/submit")
    assert response.status_code == 409


async def test_review_step_rejects_declined_terms_with_422(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "sweden", "customer_type": "private"}
    )
    application_id = create_response.json()["id"]

    await client.put(
        f"/api/v1/applications/{application_id}/steps/personal_info",
        json={"personal_identity_number": "199001011234"},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/address_info",
        json={
            "email": "a@example.com",
            "phone": "+46701234567",
            "address_line1": "Main st 1",
            "city": "Stockholm",
            "postal_code": "11122",
        },
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/consent",
        json={"consent_given": True, "pep_sanctions_declaration": True, "tax_residency": "SE"},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/employment_income",
        json={"employment_status": "employed", "monthly_income": 30000, "household_size": 2},
    )
    await client.put(f"/api/v1/applications/{application_id}/steps/credit_decision", json={})

    response = await client.put(
        f"/api/v1/applications/{application_id}/steps/review_submit",
        json={"accept_terms": False},
    )
    assert response.status_code == 422


async def test_poland_business_clean_identifiers_are_approved_on_submit(client):
    create_response = await client.post(
        "/api/v1/applications", json={"country": "poland", "customer_type": "business"}
    )
    application_id = create_response.json()["id"]

    await client.put(
        f"/api/v1/applications/{application_id}/steps/organisation_info",
        json={"nip": "1234567890", "regon_or_krs_ceidg_identifier": "123456789", "legal_form": "sp. z o.o."},
    )
    await client.put(f"/api/v1/applications/{application_id}/steps/registry_lookup", json={})
    await client.put(
        f"/api/v1/applications/{application_id}/steps/authority_confirmation",
        json={"representative_identifier": "90010112345", "authority_confirmed": True},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/beneficial_owners",
        json={"owners": [{"name": "Jan Kowalski", "identifier": "80010112345", "ownership_percentage": 100}]},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/vat_tax_status",
        json={"vat_tax_status": "active", "business_activity": "retail", "expected_usage": "domestic trade"},
    )
    await client.put(
        f"/api/v1/applications/{application_id}/steps/kyb_credit_bank_validation",
        json={"iban": "PL12345678901234567890"},
    )
    last_step_response = await client.put(
        f"/api/v1/applications/{application_id}/steps/review_sign",
        json={"accept_terms": True},
    )
    assert last_step_response.status_code == 200

    submit_response = await client.put(f"/api/v1/applications/{application_id}/submit")
    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == ApplicationStatus.APPROVED.value
