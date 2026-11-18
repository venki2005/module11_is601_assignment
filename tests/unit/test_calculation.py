import uuid
import pytest
from pydantic import ValidationError
from app.models.calculation import (
    Calculation,
    AddCalculation,
    SubCalculation,
    MultiplyCalculation,
    DivideCalculation,
    CalculationType,
)
from app.schemas.calculation import CalculationCreate, CalculationRead


def test_factory_creates_correct_subclasses():
    add_calc = Calculation.create("Add", 10, 5)
    assert isinstance(add_calc, AddCalculation)
    assert add_calc.result == 15

    sub_calc = Calculation.create("Sub", 10, 5)
    assert isinstance(sub_calc, SubCalculation)
    assert sub_calc.result == 5

    mul_calc = Calculation.create("Multiply", 10, 5)
    assert isinstance(mul_calc, MultiplyCalculation)
    assert mul_calc.result == 50

    div_calc = Calculation.create("Divide", 10, 5)
    assert isinstance(div_calc, DivideCalculation)
    assert div_calc.result == 2.0


def test_factory_case_insensitive_normalization():
    calc = Calculation.create("  multiply ", 3, 4)
    assert isinstance(calc, MultiplyCalculation)
    assert calc.result == 12


def test_factory_invalid_type_raises_value_error():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        Calculation.create("Modulus", 10, 3)


def test_factory_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        Calculation.create("Divide", 10, 0)


def test_calculation_create_valid_with_uuid():
    uid = uuid.uuid4()
    schema = CalculationCreate(a=20, b=4, type="divide", user_id=uid)
    assert schema.type == CalculationType.DIVIDE
    assert schema.user_id == uid


def test_calculation_create_rejects_zero_divisor():
    with pytest.raises(ValidationError) as exc_info:
        CalculationCreate(a=10, b=0, type="Divide")
    assert "Division by zero is not allowed" in str(exc_info.value)


def test_calculation_create_rejects_invalid_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=5, type="Power")


def test_calculation_create_rejects_non_numeric_operands():
    with pytest.raises(ValidationError):
        CalculationCreate(a="invalid", b=5, type="Add")


def test_calculation_read_serialization():
    uid = uuid.uuid4()
    calc = Calculation.create("Add", 7.5, 2.5, user_id=uid)
    calc.id = 101
    read_schema = CalculationRead.model_validate(calc)
    assert read_schema.id == 101
    assert read_schema.result == 10.0
    assert read_schema.type == CalculationType.ADD
    assert read_schema.user_id == uid