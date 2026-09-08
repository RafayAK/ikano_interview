from sqlalchemy import select

from app.db.models import OnboardingApplication
from app.domain.enums import Country, CustomerType


async def test_insert_and_read_application(db_session):
    app_row = OnboardingApplication(country=Country.SWEDEN, customer_type=CustomerType.PRIVATE)
    db_session.add(app_row)
    await db_session.flush()

    result = await db_session.execute(
        select(OnboardingApplication).where(OnboardingApplication.id == app_row.id)
    )
    fetched = result.scalar_one()
    assert fetched.country == Country.SWEDEN
    assert fetched.customer_type == CustomerType.PRIVATE


async def test_previous_test_data_was_rolled_back(db_session):
    result = await db_session.execute(select(OnboardingApplication))
    assert result.scalars().all() == []
