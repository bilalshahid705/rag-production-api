from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class ChatRequest(SQLModel):
    message: str = Field(
        min_length=1,
        max_length=10000,
        description="The user message to the agent",
    )
    #thread_id is attached to each conversion.
    thread_id: str = Field(
        default="default",
        description="Conversation thread ID",
    )

class ChatResponse(SQLModel):
    response: str
    thread_id: str
    model_used: str
    cache: bool = False
    processing_time_ms: float
    # default_factory calls a function to generate the default value.
    # lambda is an anonymous function that returns the current datetime.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(SQLModel):
    status: str = "healthy"
    environment: str
    version: str = "1.0.0"
    checks: dict = {}


# This is a informational response about the system.
class MetricsResponse(SQLModel):
    total_requests: int
    total_errors: int
    error_rate: str
    avg_latency_ms: int
    cache_hit_rate: str
    total_input_tokens: int
    total_output_tokens: int


class ErrorResponse(SQLModel):
    error: str
    detail: str | None = None
    request_id: str | None = None
