import enum
import uuid
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CalculationType(str, enum.Enum):
    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)
    result = Column(Float, nullable=True)

    # Matches User.id (UUID) in app/models/user.py
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    user = relationship("User", back_populates="calculations")

    __mapper_args__ = {
        "polymorphic_identity": "calculation",
        "polymorphic_on": type,
    }

    def get_result(self) -> float:
        raise NotImplementedError("Subclasses must implement get_result()")

    @classmethod
    def create(
        cls,
        calc_type: str,
        a: float,
        b: float,
        user_id: uuid.UUID | None = None,
    ) -> "Calculation":
        """Factory method to instantiate the appropriate Calculation subclass and compute result."""
        normalized_type = (
            calc_type.strip().capitalize() if isinstance(calc_type, str) else calc_type
        )

        subclasses = {
            CalculationType.ADD.value: AddCalculation,
            CalculationType.SUB.value: SubCalculation,
            CalculationType.MULTIPLY.value: MultiplyCalculation,
            CalculationType.DIVIDE.value: DivideCalculation,
        }

        target_class = subclasses.get(normalized_type)
        if not target_class:
            raise ValueError(f"Unsupported calculation type: {calc_type}")

        instance = target_class(a=a, b=b, type=normalized_type, user_id=user_id)
        instance.result = instance.get_result()
        return instance


class AddCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": CalculationType.ADD.value}

    def get_result(self) -> float:
        return self.a + self.b


class SubCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": CalculationType.SUB.value}

    def get_result(self) -> float:
        return self.a - self.b


class MultiplyCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": CalculationType.MULTIPLY.value}

    def get_result(self) -> float:
        return self.a * self.b


class DivideCalculation(Calculation):
    __mapper_args__ = {"polymorphic_identity": CalculationType.DIVIDE.value}

    def get_result(self) -> float:
        if self.b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return self.a / self.b