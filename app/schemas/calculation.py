from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from app.models.calculation import CalculationType


class CalculationBase(BaseModel):
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")
    type: CalculationType = Field(
        ...,
        description="Operation type: Add, Sub, Multiply, or Divide",
    )

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().capitalize()
        return value


class CalculationCreate(CalculationBase):
    user_id: Optional[UUID] = Field(
        default=None,
        description="Optional UUID foreign key of the user creating the calculation",
    )

    @model_validator(mode="after")
    def validate_division_by_zero(self) -> "CalculationCreate":
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError(
                "Division by zero is not allowed (b cannot be 0 when type is Divide)."
            )
        return self


class CalculationRead(CalculationBase):
    id: int = Field(..., description="Unique calculation ID")
    result: float = Field(..., description="Computed result of the calculation")
    user_id: Optional[UUID] = Field(
        default=None,
        description="Optional UUID of the user who owns this calculation",
    )

    model_config = ConfigDict(from_attributes=True)


CalculationResponse = CalculationRead