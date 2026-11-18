```markdown
# Reflection: Calculation Model, Factory Pattern, Pydantic Validation & CI/CD Pipeline

### 1. Key Architectural & Design Decisions

- **Polymorphic Calculation Modeling & Factory Pattern**: Implemented the `Calculation` SQLAlchemy model using Single Table Inheritance (`polymorphic_on=type`) with specialized subclasses (`AddCalculation`, `SubCalculation`, `MultiplyCalculation`, and `DivideCalculation`). A class-level `Calculation.create()` factory method encapsulates subclass instantiation, normalizes operation strings, computes the result upon creation, and raises clear errors for unsupported operations or division by zero.
- **Persistent Result Storage vs. On-Demand Computation**: Stored the computed `result` column directly in PostgreSQL during creation so historical calculations can be queried, audited, and serialized efficiently without recomputing values on every read, while retaining `get_result()` on each subclass for polymorphic verification.
- **Pydantic v2 Validation & Serialization**: Built `CalculationCreate` with a pre-validator (`@field_validator("type", mode="before")`) to normalize operation casing and a model validator (`@model_validator(mode="after")`) to reject zero divisors before any database transaction begins. Separated output serialization into `CalculationRead` (`from_attributes=True`) to keep response contracts explicit and safe.
- **Relational Integrity with UUID Foreign Keys**: Linked `Calculation.user_id` to `users.id` (`UUID(as_uuid=True)`) with `ondelete="CASCADE"` and bidirectional ORM relationships (`User.calculations` and `Calculation.user`), ensuring referential integrity in PostgreSQL.

### 2. Testing & CI/CD Workflow

- **Comprehensive Unit & Integration Coverage**: Added dedicated unit tests (`tests/unit/test_calculation.py`) verifying factory subclass selection, case-insensitive input normalization, and Pydantic schema rejections, alongside PostgreSQL integration tests (`tests/integration/test_calculation_integration.py`) verifying record persistence, valid user foreign key associations, and `IntegrityError` handling for nonexistent user IDs.
- **Database Integration in CI**: Leveraged a live PostgreSQL 15 service container (`app_db`) in GitHub Actions to execute all 87 unit, integration, and end-to-end tests against an authentic relational database engine[cite: 7].
- **Security Scanning & Multi-Architecture Deployment**: Maintained a three-stage GitHub Actions pipeline (`test` -> `security` -> `deploy`) that scans the built container image with Trivy before pushing multi-architecture (`linux/amd64`, `linux/arm64`) images to `vrv7222/601_module11` on Docker Hub[cite: 7].

### 3. Challenges & Resolutions

- **Foreign Key Type Alignment (`UUID` vs. `Integer`)**: Discovered that the existing `User` model primary key uses PostgreSQL `UUID(as_uuid=True)` rather than an auto-incrementing integer. Updated `Calculation.user_id` and the Pydantic `CalculationCreate` / `CalculationRead` schemas to use `UUID` so PostgreSQL foreign key constraints matched cleanly.
- **Local Test Database & Virtual Environment Isolation**: Rebuilt the project virtual environment cleanly under Python 3.12 and initialized the `app_db` database inside the local PostgreSQL container so SQLAlchemy session fixtures could tear down and recreate tables reliably.
- **Asynchronous DOM Updates in Playwright E2E Tests**: Resolved race conditions in `tests/e2e/test_e2e.py` where immediate `inner_text()` checks ran before frontend `fetch()` calls completed by switching assertions to Playwright's auto-waiting `expect(page.locator("#result")).to_have_text(...)`.
```
