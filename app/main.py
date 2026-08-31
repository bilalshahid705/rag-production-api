import time
import os 
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from langsmith import traceable
from dotenv import load_dotenv

from app import security
from app.config import get_settings
from app.schemas import (ChatRequest, ChatResponse, HealthResponse, MetricsResponse, ErrorResponse)
from app.security.security_pipeline import SecurityPipeline
from app.cache.response_cache import ResponseCache
from app.monitoring import get_logger, MetricsCollector, RequestTimer
from app.agent import ProductionAgent

load_dotenv()

cache: ResponseCache = None
metrics: MetricsCollector = None
agent: ProductionAgent = None
security: SecurityPipeline = None
logger = get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):

    global security, cache, metrics, agent

    settings = get_settings()

    logger.info("Starting production API...", extra= {"extra_data": {
        "environment": settings.app_env, 
        "primary_model": settings.primary_model,
        "tracing_enabled": settings.langsmith_tracing,
        }})

    security = SecurityPipeline()
    cache = ResponseCache(ttl_seconds=settings.cache_ttl_seconds)
    metrics = MetricsCollector()
    agent = ProductionAgent()

    logger.info("All components initailized. Ready to serve requests.")

    yield

    logger.info("Shutting down...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Production LangGraph API",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded,
):
    logger.warning(
        "Rate limit exceeded",
        extra={
            "extra_data": {
                "path": request.url.path,
                "method": request.method,
                "client": get_remote_address(request),
            }
        },
    )

    return JSONResponse(
        status_code=429,
        content={ 
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "path": request.url.path,
        },
    )

@app.post("/chat", response_model=ChatResponse)
@limiter.limit(lambda: get_settings().rate_limit)
@traceable(name="chat_endpoint")
async def chat(request: Request, body: ChatRequest):

    with RequestTimer() as timer:
        security_notes = []


        # Step 1: Security Check
        is_allowed, cleaned_message, notes = security.CheckInput(body.message)
        security_notes.extend(notes)

        if not is_allowed:
            logger.warning("Request blocked by security", extra={"extra_data": {
                "reason": notes,
                "thread_id": body.thread_id, 
            }})
            metrics.record_request(latency_ms=0, error=True)
            raise HTTPException(
                status_code = 400,
                detail = "Your message was blocked by our filters."
            )

        # Step 2: Cache Lookup

        cached_response = cache.GetCache(cleaned_message)
        if cached_response is not None:
            metrics.record_request(latency_ms=0, cache_hit=True)
            logger.info("Cache hit", extra={"extra_data": {
                "thread_id": body.thread_id, 
            }})

            return ChatResponse(
                response=cached_response,
                thread_id=body.thread_id,
                model_used="cache",
                processing_time_ms=0
            )

        # Step 3: Invoke LangGraph Agent

        try:
            result = agent.invoke_agent(cleaned_message)
        except Exception as e:
            logger.info(f"Agent invocation failed: {e}", extra={"extra_data": {
                "thread_id": body.thread_id, 
                "error": str(e)
            }})
            metrics.record_request(latency_ms=0, error=True)
            raise HTTPException(
                status_code = 500,
                detail = "An error occured while processing your request."
            )

        response_text = result["response"]
        model_used = result["model_used"]

        # Step 4: Output Validation

        validation_response, output_warning = security.CheckOutput(response_text)
        security_notes.extend(output_warning)

        # Step 5: Cache Store

        cache.SetCache(cleaned_message, validation_response)

    # Step 6: Log & Record Metrics
    input_token = int(len(cleaned_message.split()) * 1.3)
    output_token = int(len(validation_response.split()) * 1.3)

    metrics.record_request(
        latency_ms=timer.elapsed_ms,
        input_tokens=input_token,
        output_tokens=output_token,
        cache_hit=False,
    )

    if security_notes:
        logger.info("Security notes", extra={"extra_data": {
            "notes": security_notes,
            "thread_id": body.thread_id
        }})
    
    logger.info("Request Completed", extra={"extra_data": {
        "thread_id": body.thread_id,
        "model_used": model_used,
        "latency_ms": round(timer.elapsed_ms, 2),
    }})

    return ChatResponse(
        response=validation_response,
        thread_id=body.thread_id,
        model_used=model_used,
        processing_time_ms=round(timer.elapsed_ms, 2)
    )



@app.get("/health", response_model=HealthResponse)
async def health():
    settings = get_settings()

    checks = {
        "agent": agent is not None,
        "security": security is not None,
        "cache": cache is not None,
    }

    all_healthy = all(checks.values())

    return HealthResponse(
        status="healthy" if all_healthy else "degraded",
        environment=settings.app_env,
        checks=checks,
    )


@app.get("/metrics", response_model=MetricsResponse)
async def getMetrics():
    summary = metrics.get_summary
    return MetricsResponse(**summary)

@app.get("/cache/stats")
async def cache_stats():
    return cache.stats