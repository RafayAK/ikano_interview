class FlowNotFoundError(Exception):
    def __init__(self, country, customer_type):
        self.country = country
        self.customer_type = customer_type
        super().__init__(f"No flow found for country={country} and customer_type={customer_type}")


class ApplicationNotFoundError(Exception):
    def __init__(self, application_id):
        self.application_id = application_id
        super().__init__(f"No application found with id={application_id}")


class ResumeTokenInvalidError(Exception):
    def __init__(self):
        super().__init__("Resume token is missing, invalid, or expired")


class InvalidStepTransitionError(Exception):
    def __init__(self, requested_step_id: str, current_step_id: str | None):
        self.requested_step_id = requested_step_id
        self.current_step_id = current_step_id
        super().__init__(
            f"Cannot complete step '{requested_step_id}'; "
            f"current actionable step is '{current_step_id}'"
        )


class StepSchemaNotFoundError(Exception):
    def __init__(self, country, customer_type, step_id):
        self.country = country
        self.customer_type = customer_type
        self.step_id = step_id
        super().__init__(
            f"No input schema registered for country={country}, "
            f"customer_type={customer_type}, step_id={step_id}"
        )


class ApplicationAlreadyFinalizedError(Exception):
    def __init__(self, application_id):
        self.application_id = application_id
        super().__init__(f"Application {application_id} has already been finalized")


class ApplicationNotReadyForSubmissionError(Exception):
    def __init__(self, application_id, remaining_step_id: str):
        self.application_id = application_id
        self.remaining_step_id = remaining_step_id
        super().__init__(
            f"Application {application_id} still has an incomplete step: {remaining_step_id}"
        )

