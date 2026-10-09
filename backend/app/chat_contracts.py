"""Question, intent, structured model output and HTTP response contracts."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .chat_models import QueryProposal, Scalar

SIMULATED_LABEL = 'Simulated course rates and availability—not real booking information'


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)


class ChatRequest(StrictModel):
    question: str = Field(min_length=1, max_length=2000)

    @field_validator('question')
    @classmethod
    def clean_question(cls, value):
        if not value.strip() or '\x00' in value or len(value.encode('utf-8')) > 8000:
            raise ValueError('Enter a question of 1–2000 characters.')
        return value


class StayIntent(StrictModel):
    postcode: str = Field(pattern=r'^[0-9]{5}$')
    check_in: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    check_out: str = Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    rooms: int = Field(ge=1, le=10)
    budget_cents: int | None = Field(ge=0, le=100_000_000)
    budget_type: Literal['none', 'total_stay', 'nightly_per_room']


class QueryDecision(StrictModel):
    kind: Literal['query', 'clarification']
    intent: StayIntent | None
    proposal: QueryProposal | None
    clarification: str | None = Field(max_length=500)


class Recommendation(StrictModel):
    hotel_id: str = Field(min_length=1, max_length=2048)
    reason: Literal['lowest_total', 'more_rooms', 'meets_requirements']


class AnswerDecision(StrictModel):
    status: Literal['answer', 'no_matches', 'insufficient_data']
    recommendations: list[Recommendation] = Field(max_length=10)


class ChatResponse(StrictModel):
    status: Literal['answer', 'no_matches', 'insufficient_data', 'clarification']
    answer: str
    simulated_label: str = SIMULATED_LABEL
    hotels: list[dict]
    evidence: dict
