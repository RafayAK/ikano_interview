from dataclasses import dataclass

from app.domain.enums import Country, CustomerType


@dataclass(frozen=True)
class StepDefinition:
    id: str
    title: str

@dataclass(frozen=True)
class FlowDefinition:
    country: Country
    customer_type: CustomerType

    # Use a tuple to ensure immutability, this would make the data look like
    # e.g. FlowDefinition(country=Country.SWEDEN, customer_type=CustomerType.INDIVIDUAL, steps=(StepDefinition(id="personal_info", title="Personal Information"), StepDefinition(id="address_info", title="Address Information"), StepDefinition(id="document_upload", title="Document Upload"), StepDefinition(id="review_submit", title="Review and Submit")))
    # the three dots indicate that the tuple can contain any number of StepDefinition instances, but they cannot be modified after creation.
    steps: tuple[StepDefinition, ...]

    @property
    def step_ids(self) -> tuple[str, ...]:
        return tuple(step.id for step in self.steps)

    @property
    def first_step(self) -> StepDefinition:
        return self.steps[0]

    def position(self, step_id: str) -> int:
        for index, step in enumerate(self.steps):
            if step.id == step_id:
                return index + 1  # Position is 1-based
        raise ValueError(f"Step ID '{step_id}' not found in flow definition.")

    def get_step(self, step_id: str) -> StepDefinition:
        for step in self.steps:
            if step.id == step_id:
                return step
        raise ValueError(f"Step ID '{step_id}' not found in flow definition.")

    def next_step(self, current_step_id: str) -> StepDefinition | None:
        for index, step in enumerate(self.steps):
            if step.id == current_step_id:
                if index + 1 < len(self.steps):
                    return self.steps[index + 1]
                else:
                    return None  # No next step
        raise ValueError(f"Step ID '{current_step_id}' not found in flow definition.")