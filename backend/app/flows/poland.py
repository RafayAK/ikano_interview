from app.flows.base import StepDefinition, FlowDefinition
from app.domain.enums import Country, CustomerType

# Private individual onboarding
# 1. Choose Poland + private individual
# 2. Collect PESEL and initiate eID/Trusted Profile/mObywatel-style identity mock
# 3. Confirm contact details and registered address
# 4. Capture consent and PEP/sanctions declaration
# 5. Collect employment, income and affordability information
# 6. Run BIK-style credit-bureau mock and decision rules
# 7. Review summary, accept terms, submit application

# Note for later:
# PESEL: 11 digits

POLAND_PRIVATE_FLOW = FlowDefinition(
    country=Country.POLAND,
    customer_type=CustomerType.PRIVATE,
    steps=(
        StepDefinition(id="personal_info", title="Personal Information"),  # step 2 in the pdf
        StepDefinition(id="address_info", title="Contact Details and Registered Address"),  # step 3 in the pdf
        StepDefinition(id="consent", title="Consent and PEP/Sanctions Declaration"),  # step 4 in the pdf
        StepDefinition(id="employment_income", title="Employment, Income and Affordability Information"),  # step 5 in the pdf
        StepDefinition(id="credit_decision", title="BIK-Style Credit-Bureau Mock and Decision Rules"),  # step 6 in the pdf
        StepDefinition(id="review_submit", title="Review and Submit"),  # step 7 in the pdf
    ),
)


# Business onboarding
# 1. Choose Poland + business
# 2. Collect NIP, REGON or KRS/CEIDG identifier and legal form
# 3. Run CEIDG/KRS-style registry lookup
# 4. Confirm board member or sole proprietor authority
# 5. Collect beneficial owners and verify identity/risk
# 6. Capture VAT/tax status, business activity and expected usage
# 7. Run KYB, sanctions/PEP, business credit and bank-account validation, then review/sign

# NOTE: for later: NIP, REGON, KRS, and CEIDG are the four primary identification and registration systems used for businesses operating in Poland.
# NIP: 10 digits
# REGON: 9 digits or 14 digits
# KRS: 10 digits
# CEIDG: not a number CEIDG is the register database itself. It does not issue a unique ID; businesses in CEIDG use their NIP and REGON numbers.
POLAND_BUSINESS_FLOW = FlowDefinition(
    country=Country.POLAND,
    customer_type=CustomerType.BUSINESS,
    steps=(
        StepDefinition(id="organisation_info", title="Organisation Information"),  # step 2 in the pdf
        StepDefinition(id="registry_lookup", title="Registry Lookup"),  # step 3 in the pdf
        StepDefinition(id="authority_confirmation", title="Board Member or Sole Proprietor Authority"),  # step 4 in the pdf
        StepDefinition(id="beneficial_owners", title="Beneficial Owners and Identity/Risk Verification"),  # step 5 in the pdf
        StepDefinition(id="vat_tax_status", title="VAT/Tax Status, Business Activity and Expected Usage"),  # step 6 in the pdf
        StepDefinition(id="kyb_credit_bank_validation", title="KYB, Sanctions/PEP, Business Credit and Bank-Account Validation"),  # step 7a in the pdf
        StepDefinition(id="review_sign", title="Review and Sign"),  # step 7b in the pdf
    ),
)