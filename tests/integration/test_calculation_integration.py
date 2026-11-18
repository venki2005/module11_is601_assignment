import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.calculation import Calculation, AddCalculation, DivideCalculation
from app.schemas.calculation import CalculationCreate, CalculationRead


def test_insert_and_query_calculation(db_session):
    # Validate input via Pydantic schema
    schema_in = CalculationCreate(a=30, b=6, type="Divide")

    # Instantiate via Factory & save to PostgreSQL
    calc = Calculation.create(
        calc_type=schema_in.type.value,
        a=schema_in.a,
        b=schema_in.b,
    )
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    assert calc.id is not None
    assert calc.result == 5.0

    # Query back from DB & verify polymorphic class loading
    stored = db_session.query(Calculation).filter(Calculation.id == calc.id).first()
    assert stored is not None
    assert isinstance(stored, DivideCalculation)
    assert stored.get_result() == 5.0

    # Serialize with CalculationRead
    schema_out = CalculationRead.model_validate(stored)
    assert schema_out.id == calc.id
    assert schema_out.result == 5.0


def test_calculation_with_valid_user_foreign_key(db_session, test_user):
    # test_user fixture comes directly from tests/conftest.py
    calc = Calculation.create("Add", 15, 25, user_id=test_user.id)
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    assert calc.user_id == test_user.id
    assert isinstance(calc, AddCalculation)
    assert len(test_user.calculations) == 1
    assert test_user.calculations[0].result == 40.0


def test_calculation_with_nonexistent_user_fk_fails(db_session):
    fake_user_id = uuid.uuid4()
    calc = Calculation.create("Sub", 10, 3, user_id=fake_user_id)
    db_session.add(calc)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()