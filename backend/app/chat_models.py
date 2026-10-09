"""Contracts for untrusted query proposals; no transport or database access."""
import math
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

SQL_MAX_BYTES = 8192
PARAMETER_LIMIT = 32
PARAMETER_MAX_BYTES = 2048
Scalar = str | int | float | None


class QueryProposal(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, revalidate_instances='always')

    sql: str = Field(min_length=1, max_length=SQL_MAX_BYTES)
    parameters: list[Scalar] = Field(max_length=PARAMETER_LIMIT)

    @field_validator('sql')
    @classmethod
    def bounded_sql(cls, value):
        if not value.strip() or '\x00' in value or len(value.encode('utf-8')) > SQL_MAX_BYTES:
            raise ValueError('Invalid SQL text.')
        return value

    @field_validator('parameters', mode='before')
    @classmethod
    def bounded_parameters(cls, values):
        if type(values) is not list:
            raise ValueError('Parameters must be an array.')
        for value in values:
            if type(value) not in (str, int, float, type(None)):
                raise ValueError('Parameters must be JSON scalars, excluding booleans.')
            if type(value) is str and len(value.encode('utf-8')) > PARAMETER_MAX_BYTES:
                raise ValueError('Parameter is too long.')
            if type(value) is int and not -(2**63) <= value < 2**63:
                raise ValueError('Integer is outside SQLite range.')
            if type(value) is float and not math.isfinite(value):
                raise ValueError('Number must be finite.')
        return values


class QueryRecords(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)

    columns: list[str]
    records: list[dict[str, Scalar]]
    row_count: Annotated[int, Field(ge=0, le=50)]
    row_limit: int = 50
    # No partial results are returned on overflow. A SQL LIMIT still narrows scope.
    result_bytes: int
