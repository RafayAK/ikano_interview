from pydantic import BaseModel, Field, field_validator

from app.domain.enums import Country, CustomerType
from app.domain.errors import StepSchemaNotFoundError


class EmptyStepInput(BaseModel):
    """For steps that only trigger a check using data already collected earlier."""


class ReviewInput(BaseModel):
    accept_terms: bool

    @field_validator("accept_terms")
    @classmethod
    def must_accept(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Terms must be accepted to proceed.")
        return value


# --- Private: identity ---


class SwedenPrivateIdentityInput(BaseModel):
    personal_identity_number: str = Field(min_length=10, max_length=13)


class SpainPrivateIdentityInput(BaseModel):
    dni_or_nie: str = Field(min_length=8, max_length=9)


class PolandPrivateIdentityInput(BaseModel):
    pesel: str = Field(min_length=11, max_length=11)


# --- Private: contact/address ---


class SwedenPrivateAddressInput(BaseModel):
    email: str
    phone: str
    address_line1: str
    city: str
    postal_code: str


class SpainPrivateAddressInput(BaseModel):
    email: str
    phone: str
    address_line1: str
    city: str
    province: str
    postal_code: str
    tax_residency: str


class PolandPrivateAddressInput(BaseModel):
    email: str
    phone: str
    address_line1: str
    city: str
    postal_code: str


# --- Private: consent ---


class SwedenPrivateConsentInput(BaseModel):
    consent_given: bool
    pep_sanctions_declaration: bool
    tax_residency: str


class SpainPrivateConsentInput(BaseModel):
    consent_given: bool
    pep_sanctions_declaration: bool


class PolandPrivateConsentInput(BaseModel):
    consent_given: bool
    pep_sanctions_declaration: bool


# --- Private: employment/income ---


class SwedenPrivateEmploymentInput(BaseModel):
    employment_status: str
    monthly_income: float = Field(gt=0)
    household_size: int = Field(ge=1)


class SpainPrivateEmploymentInput(BaseModel):
    employment_status: str
    monthly_income: float = Field(gt=0)
    housing_costs: float = Field(ge=0)
    dependants: int = Field(ge=0)


class PolandPrivateEmploymentInput(BaseModel):
    employment_status: str
    monthly_income: float = Field(gt=0)


# --- Business: organisation/company info ---


class SwedenBusinessOrganisationInput(BaseModel):
    organisation_number: str
    legal_name: str
    legal_form: str


class SpainBusinessCompanyInput(BaseModel):
    company_nif: str
    legal_form: str
    registered_address: str


class PolandBusinessOrganisationInput(BaseModel):
    nip: str
    regon_or_krs_ceidg_identifier: str
    legal_form: str


# --- Business: authority/representative ---


class SwedenBusinessRepresentativeInput(BaseModel):
    representative_identifier: str
    signatory_rights: bool


class SpainBusinessRepresentativeInput(BaseModel):
    representative_identifier: str


class PolandBusinessRepresentativeInput(BaseModel):
    representative_identifier: str
    authority_confirmed: bool


# --- Business: beneficial owners (shared step id across all 3 countries) ---


class BeneficialOwner(BaseModel):
    name: str
    identifier: str
    ownership_percentage: float | None = Field(default=None, ge=0, le=100)


class BeneficialOwnersInput(BaseModel):
    owners: list[BeneficialOwner] = Field(min_length=1)


# --- Business: business profile ---


class SwedenBusinessActivityInput(BaseModel):
    business_activity: str
    turnover: float = Field(ge=0)
    purpose: str
    expected_usage: str


class SpainBusinessSectorInput(BaseModel):
    sector: str
    turnover: float = Field(ge=0)
    vat_tax_details: str
    expected_usage: str


class PolandBusinessVatTaxInput(BaseModel):
    vat_tax_status: str
    business_activity: str
    expected_usage: str


# --- Business: final KYB/credit(+bank) trigger step ---


class SpainBusinessKybCreditInput(BaseModel):
    iban: str


class PolandBusinessKybCreditInput(BaseModel):
    iban: str


STEP_INPUT_SCHEMAS: dict[tuple[Country, CustomerType, str], type[BaseModel]] = {
    # Sweden private
    (Country.SWEDEN, CustomerType.PRIVATE, "personal_info"): SwedenPrivateIdentityInput,
    (Country.SWEDEN, CustomerType.PRIVATE, "address_info"): SwedenPrivateAddressInput,
    (Country.SWEDEN, CustomerType.PRIVATE, "consent"): SwedenPrivateConsentInput,
    (Country.SWEDEN, CustomerType.PRIVATE, "employment_income"): SwedenPrivateEmploymentInput,
    (Country.SWEDEN, CustomerType.PRIVATE, "credit_decision"): EmptyStepInput,
    (Country.SWEDEN, CustomerType.PRIVATE, "review_submit"): ReviewInput,
    # Spain private
    (Country.SPAIN, CustomerType.PRIVATE, "personal_info"): SpainPrivateIdentityInput,
    (Country.SPAIN, CustomerType.PRIVATE, "address_info"): SpainPrivateAddressInput,
    (Country.SPAIN, CustomerType.PRIVATE, "consent"): SpainPrivateConsentInput,
    (Country.SPAIN, CustomerType.PRIVATE, "employment_income"): SpainPrivateEmploymentInput,
    (Country.SPAIN, CustomerType.PRIVATE, "credit_decision"): EmptyStepInput,
    (Country.SPAIN, CustomerType.PRIVATE, "review_submit"): ReviewInput,
    # Poland private
    (Country.POLAND, CustomerType.PRIVATE, "personal_info"): PolandPrivateIdentityInput,
    (Country.POLAND, CustomerType.PRIVATE, "address_info"): PolandPrivateAddressInput,
    (Country.POLAND, CustomerType.PRIVATE, "consent"): PolandPrivateConsentInput,
    (Country.POLAND, CustomerType.PRIVATE, "employment_income"): PolandPrivateEmploymentInput,
    (Country.POLAND, CustomerType.PRIVATE, "credit_decision"): EmptyStepInput,
    (Country.POLAND, CustomerType.PRIVATE, "review_submit"): ReviewInput,
    # Sweden business
    (Country.SWEDEN, CustomerType.BUSINESS, "organisation_info"): SwedenBusinessOrganisationInput,
    (Country.SWEDEN, CustomerType.BUSINESS, "company_registry_lookup"): EmptyStepInput,
    (Country.SWEDEN, CustomerType.BUSINESS, "authorised_representative"): SwedenBusinessRepresentativeInput,
    (Country.SWEDEN, CustomerType.BUSINESS, "beneficial_owners"): BeneficialOwnersInput,
    (Country.SWEDEN, CustomerType.BUSINESS, "business_activity"): SwedenBusinessActivityInput,
    (Country.SWEDEN, CustomerType.BUSINESS, "kyb_credit_decision"): EmptyStepInput,
    (Country.SWEDEN, CustomerType.BUSINESS, "review_sign"): ReviewInput,
    # Spain business
    (Country.SPAIN, CustomerType.BUSINESS, "company_info"): SpainBusinessCompanyInput,
    (Country.SPAIN, CustomerType.BUSINESS, "registro_mercantil"): EmptyStepInput,
    (Country.SPAIN, CustomerType.BUSINESS, "legal_representative_verification"): SpainBusinessRepresentativeInput,
    (Country.SPAIN, CustomerType.BUSINESS, "beneficial_owners"): BeneficialOwnersInput,
    (Country.SPAIN, CustomerType.BUSINESS, "sector_turnover"): SpainBusinessSectorInput,
    (Country.SPAIN, CustomerType.BUSINESS, "kyb_credit_iban"): SpainBusinessKybCreditInput,
    (Country.SPAIN, CustomerType.BUSINESS, "review_sign"): ReviewInput,
    # Poland business
    (Country.POLAND, CustomerType.BUSINESS, "organisation_info"): PolandBusinessOrganisationInput,
    (Country.POLAND, CustomerType.BUSINESS, "registry_lookup"): EmptyStepInput,
    (Country.POLAND, CustomerType.BUSINESS, "authority_confirmation"): PolandBusinessRepresentativeInput,
    (Country.POLAND, CustomerType.BUSINESS, "beneficial_owners"): BeneficialOwnersInput,
    (Country.POLAND, CustomerType.BUSINESS, "vat_tax_status"): PolandBusinessVatTaxInput,
    (Country.POLAND, CustomerType.BUSINESS, "kyb_credit_bank_validation"): PolandBusinessKybCreditInput,
    (Country.POLAND, CustomerType.BUSINESS, "review_sign"): ReviewInput,
}


def get_step_input_schema(
    country: Country, customer_type: CustomerType, step_id: str
) -> type[BaseModel]:
    try:
        return STEP_INPUT_SCHEMAS[(country, customer_type, step_id)]
    except KeyError as exc:
        raise StepSchemaNotFoundError(country, customer_type, step_id) from exc
