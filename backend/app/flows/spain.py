from app.flows.base import StepDefinition, FlowDefinition
from app.domain.enums import Country, CustomerType

# Private individual onboarding
# 1. Choose Spain + private individual
# 2. Collect DNI/NIE and initiate Clave/DNIe/document-verification mock
# 3. Confirm contact details, province, address, and tax residency
# 4. Capture consent and PEP/sanctions declaration
# 5. Collect employment, income, housing costs and dependants
# 6. Run credit-bureau and affordability decision
# 7. Review summary, accept terms, submit application

SPAIN_PRIVATE_FLOW = FlowDefinition(
    country=Country.SPAIN,
    customer_type=CustomerType.PRIVATE,
    steps=(
        StepDefinition(id="personal_info", title="Personal Information"),  # step 2 in the pdf
        StepDefinition(id="address_info", title="Contact Details, Province, Address, and Tax Residency"),  # step 3 in the pdf
        StepDefinition(id="consent", title="Consent and PEP/Sanctions Declaration"),  # step 4 in the pdf
        StepDefinition(id="employment_income", title="Employment, Income, Housing Costs and Dependants"),  # step 5 in the pdf
        StepDefinition(id="credit_decision", title="Credit-Bureau and Affordability Decision"),  # step 6 in the pdf
        StepDefinition(id="review_submit", title="Review and Submit"),  # step 7 in the pdf
    ),
)   




# # Business onboarding
# 1. Choose Spain + business
# 2. Collect company NIF, legal form and registered address
# 3. Run Registro Mercantil / tax-status-style lookup
# 4. Verify legal representative using DNI/NIE identity mock
# 5. Collect beneficial owners and ownership percentages
# 6. Capture sector, turnover, VAT/tax details and expected usage
# 7. Run KYB, sanctions/PEP, business credit and IBAN verification, then review/sign

SPAIN_BUSINESS_FLOW = FlowDefinition(
    country=Country.SPAIN,
    customer_type=CustomerType.BUSINESS,
    steps=(
        StepDefinition(id="company_info", title="Company Information"),  # step 2 in the pdf
        StepDefinition(id="registro_mercantil", title="Registro Mercantil / Tax Status Lookup"),  # step 3 in the pdf
        StepDefinition(id="legal_representative_verification", title="Legal Representative Verification"),  # step 4 in the pdf
        StepDefinition(id="beneficial_owners", title="Beneficial Owners and Ownership Percentages"),  # step 5 in the pdf
        StepDefinition(id="sector_turnover", title="Sector, Turnover, VAT/Tax Details and Expected Usage"),  # step 6 in the pdf
        StepDefinition(id="kyb_credit_iban", title="KYB, Sanctions/PEP, Business Credit and IBAN Verification"),  # step 7a in the pdf
        StepDefinition(id="review_sign", title="Review and Sign"),  # step 7b in the pdf
    ),
)