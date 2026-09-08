from app.flows.base import StepDefinition, FlowDefinition
from app.domain.enums import Country, CustomerType

# Private individual onboarding
# 1. Choose Sweden + private individual
# 2. Collect personal identity number and initiate BankID-style identity check
# 3. Confirm contact details and address
# 4. Capture consent, PEP/sanctions declaration, and tax residency
# 5. Collect employment, income, household and affordability inputs
# 6. Run credit-bureau decision and affordability rules
# 7. Review summary, accept terms, submit application

SWEDEN_PRIVATE_FLOW = FlowDefinition(
    country=Country.SWEDEN,
    customer_type=CustomerType.PRIVATE,
    steps=(
        StepDefinition(id="personal_info", title="Personal Information"),  # step 2 in the pdf
        StepDefinition(id="address_info", title="Contact Details and Address Information"),  # step 3 in the pdf
        StepDefinition(id="consent", title="Consent and Agreements"),  # step 4 in the pdf
        StepDefinition(id="employment_income", title="Employment, Income, Household and Affordability"),  # step 5 in the pdf
        StepDefinition(id="credit_decision", title="Credit-Bureau Decision and Affordability Rules"),  # step 6 in the pdf
        StepDefinition(id="review_submit", title="Review and Submit"),  # step 7 in the pdf
    ),
)


# Business onboarding
# 1. Choose Sweden + business
# 2. Collect organisation number, legal name and legal form
# 3. Run Bolagsverket-style company registry lookup
# 4. Confirm authorised representative and signatory rights
# 5. Collect beneficial owners and verify them with BankID-style KYC mock
# 6. Capture business activity, turnover, purpose and expected usage
# 7. Run KYB, sanctions/PEP and business-credit decision, then review/sign

SWEDEN_BUSINESS_FLOW = FlowDefinition(
    country=Country.SWEDEN,
    customer_type=CustomerType.BUSINESS,
    steps=(
        StepDefinition(id="organisation_info", title="Organisation Information"),  # step 2 in the pdf
        StepDefinition(id="company_registry_lookup", title="Company Registry Lookup"),  # step 3 in the pdf
        StepDefinition(id="authorised_representative", title="Authorised Representative and Signatory Rights"),  # step 4 in the pdf
        StepDefinition(id="beneficial_owners", title="Beneficial Owners and KYC Verification"),  # step 5 in the pdf
        StepDefinition(id="business_activity", title="Business Activity, Turnover, Purpose and Expected Usage"),  # step 6 in the pdf
        StepDefinition(id="kyb_credit_decision", title="KYB, Sanctions/PEP and Business-Credit Decision"),  # step 7a in the pdf
        StepDefinition(id="review_sign", title="Review and Sign"),  # step 7b in the pdf
    ),
)