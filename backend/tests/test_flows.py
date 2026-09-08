import pytest

from app.domain.enums import Country, CustomerType
from app.domain.errors import FlowNotFoundError
from app.flows.registry import FLOW_REGISTRY, get_flow
from app.flows.sweden import SWEDEN_PRIVATE_FLOW, SWEDEN_BUSINESS_FLOW
from app.flows.spain import SPAIN_PRIVATE_FLOW, SPAIN_BUSINESS_FLOW
from app.flows.poland import POLAND_PRIVATE_FLOW, POLAND_BUSINESS_FLOW

ALL_FLOWS = {
    (Country.SWEDEN, CustomerType.PRIVATE): SWEDEN_PRIVATE_FLOW,
    (Country.SWEDEN, CustomerType.BUSINESS): SWEDEN_BUSINESS_FLOW,
    (Country.SPAIN, CustomerType.PRIVATE): SPAIN_PRIVATE_FLOW,
    (Country.SPAIN, CustomerType.BUSINESS): SPAIN_BUSINESS_FLOW,
    (Country.POLAND, CustomerType.PRIVATE): POLAND_PRIVATE_FLOW,
    (Country.POLAND, CustomerType.BUSINESS): POLAND_BUSINESS_FLOW,
}
FLOW_IDS = [f"{country}-{customer_type}" for country, customer_type in ALL_FLOWS]


def test_registry_has_all_six_combinations():
    assert set(FLOW_REGISTRY) == {(c, t) for c in Country for t in CustomerType}


@pytest.mark.parametrize("country,customer_type", list(ALL_FLOWS), ids=FLOW_IDS)
def test_get_flow_resolves_expected_flow(country, customer_type):
    flow = get_flow(country, customer_type)
    assert flow is ALL_FLOWS[(country, customer_type)]
    assert flow.country == country
    assert flow.customer_type == customer_type


def test_get_flow_raises_for_unregistered_combination(monkeypatch):
    monkeypatch.delitem(FLOW_REGISTRY, (Country.SWEDEN, CustomerType.PRIVATE))
    with pytest.raises(FlowNotFoundError):
        get_flow(Country.SWEDEN, CustomerType.PRIVATE)


@pytest.mark.parametrize("flow", ALL_FLOWS.values(), ids=FLOW_IDS)
def test_flow_first_step_is_first_declared_step(flow):
    assert flow.first_step == flow.steps[0]


@pytest.mark.parametrize("flow", ALL_FLOWS.values(), ids=FLOW_IDS)
def test_flow_next_step_walks_full_chain_in_declared_order(flow):
    current = flow.first_step.id
    order = [current]
    while (nxt := flow.next_step(current)) is not None:
        order.append(nxt.id)
        current = nxt.id
    assert tuple(order) == flow.step_ids


@pytest.mark.parametrize("flow", ALL_FLOWS.values(), ids=FLOW_IDS)
def test_flow_next_step_returns_none_after_last_step(flow):
    assert flow.next_step(flow.step_ids[-1]) is None


@pytest.mark.parametrize("flow", ALL_FLOWS.values(), ids=FLOW_IDS)
def test_flow_next_step_raises_for_unknown_step(flow):
    with pytest.raises(ValueError):
        flow.next_step("not_a_real_step")


@pytest.mark.parametrize("flow", ALL_FLOWS.values(), ids=FLOW_IDS)
def test_flow_position_raises_for_unknown_step(flow):
    with pytest.raises(ValueError):
        flow.position("not_a_real_step")


@pytest.mark.parametrize("flow", ALL_FLOWS.values(), ids=FLOW_IDS)
def test_flow_has_no_duplicate_step_ids(flow):
    assert len(flow.step_ids) == len(set(flow.step_ids))


def test_business_flows_differ_meaningfully_from_private_flows():
    for country in Country:
        private = ALL_FLOWS[(country, CustomerType.PRIVATE)]
        business = ALL_FLOWS[(country, CustomerType.BUSINESS)]
        assert set(private.step_ids) != set(business.step_ids)
