from app.flows.base import StepDefinition, FlowDefinition
from app.domain.errors import FlowNotFoundError
from app.domain.enums import Country, CustomerType
from app.flows.poland import POLAND_BUSINESS_FLOW, POLAND_PRIVATE_FLOW
from app.flows.sweden import SWEDEN_PRIVATE_FLOW, SWEDEN_BUSINESS_FLOW
from app.flows.spain import SPAIN_PRIVATE_FLOW, SPAIN_BUSINESS_FLOW


FLOW_REGISTRY: dict[tuple[Country, CustomerType], FlowDefinition] = {
    (Country.SWEDEN, CustomerType.PRIVATE): SWEDEN_PRIVATE_FLOW,
    (Country.SWEDEN, CustomerType.BUSINESS): SWEDEN_BUSINESS_FLOW,
    (Country.POLAND, CustomerType.PRIVATE): POLAND_PRIVATE_FLOW,
    (Country.POLAND, CustomerType.BUSINESS): POLAND_BUSINESS_FLOW,
    (Country.SPAIN, CustomerType.PRIVATE): SPAIN_PRIVATE_FLOW,
    (Country.SPAIN, CustomerType.BUSINESS): SPAIN_BUSINESS_FLOW,

}

def get_flow(country: Country, customer_type: CustomerType) -> FlowDefinition:

    try:
        return FLOW_REGISTRY[(country, customer_type)]
    except KeyError:
        raise FlowNotFoundError(country, customer_type)
