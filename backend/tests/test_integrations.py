import pytest

from app.integrations.bank_account import BankAccountCheckRequest, BankAccountOutcome, MockBankAccountClient
from app.integrations.credit import CreditCheckRequest, CreditOutcome, MockCreditClient
from app.integrations.identity import IdentityCheckRequest, IdentityOutcome, MockIdentityClient
from app.integrations.registry import MockRegistryClient, RegistryCheckRequest, RegistryOutcome
from app.integrations.sanctions import MockSanctionsClient, SanctionsCheckRequest, SanctionsOutcome


@pytest.mark.parametrize(
    "identifier,expected",
    [
        ("199001011234", IdentityOutcome.VERIFIED),
        ("199001011000", IdentityOutcome.MANUAL_REVIEW),
        ("199001011999", IdentityOutcome.DOCUMENT_MISMATCH),
        ("199001011888", IdentityOutcome.EXPIRED_ID),
    ],
)
async def test_identity_mock_outcomes(identifier, expected):
    result = await MockIdentityClient().check(IdentityCheckRequest(identifier=identifier))
    assert result.outcome == expected


@pytest.mark.parametrize(
    "identifier,expected",
    [
        ("5560001234", RegistryOutcome.ACTIVE_COMPANY),
        ("5560001000", RegistryOutcome.DISSOLVED),
        ("5560001999", RegistryOutcome.UNKNOWN_REPRESENTATIVE),
        ("5560001888", RegistryOutcome.MISSING_UBO),
    ],
)
async def test_registry_mock_outcomes(identifier, expected):
    result = await MockRegistryClient().check(RegistryCheckRequest(identifier=identifier))
    assert result.outcome == expected


@pytest.mark.parametrize(
    "identifier,expected",
    [
        ("199001011234", SanctionsOutcome.NO_HIT),
        ("199001011000", SanctionsOutcome.POSSIBLE_HIT),
        ("199001011666", SanctionsOutcome.CONFIRMED_HIT),
    ],
)
async def test_sanctions_mock_outcomes(identifier, expected):
    result = await MockSanctionsClient().check(SanctionsCheckRequest(identifier=identifier))
    assert result.outcome == expected


@pytest.mark.parametrize(
    "identifier,expected",
    [
        ("199001011234", CreditOutcome.CLEAN),
        ("199001011000", CreditOutcome.LOW_AFFORDABILITY),
        ("199001011999", CreditOutcome.POOR_CREDIT_HISTORY),
    ],
)
async def test_credit_mock_outcomes(identifier, expected):
    result = await MockCreditClient().check(CreditCheckRequest(identifier=identifier, income=30000))
    assert result.outcome == expected


@pytest.mark.parametrize(
    "iban,expected",
    [
        ("SE1234567890123456781234", BankAccountOutcome.IBAN_VERIFIED),
        ("SE1234567890123456780000", BankAccountOutcome.UNREACHABLE),
        ("SE1234567890123456789999", BankAccountOutcome.NAME_MISMATCH),
    ],
)
async def test_bank_account_mock_outcomes(iban, expected):
    result = await MockBankAccountClient().check(BankAccountCheckRequest(iban=iban))
    assert result.outcome == expected
