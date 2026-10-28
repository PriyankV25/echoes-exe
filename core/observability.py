"""
Echoes.exe — Observability & Stage Tracing with Sentry
Tracks agent execution lifecycle across ingestion, extraction, retrieval, AI, report, and persistence.
Avoids logging source text, private data, or credentials.
"""
import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any

from config.settings import settings

logger = logging.getLogger("echoes.observability")

_sentry_initialized = False

def init_observability():
    """Initializes Sentry SDK if SENTRY_DSN is provided."""
    global _sentry_initialized
    dsn = settings.SENTRY_DSN.strip()
    if dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            sentry_sdk.init(
                dsn=dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,
                send_default_pii=False,
                release=f"echoes-exe@{settings.VERSION}",
                environment="production" if not settings.DEBUG else "development"
            )
            _sentry_initialized = True
            logger.info("Sentry observability initialized with agent tracing.")
        except Exception as e:
            logger.warning(f"Failed to initialize Sentry: {e}")
            _sentry_initialized = False
    else:
        logger.info("SENTRY_DSN omitted. Running in local stage tracing mode.")


@contextmanager
def trace_stage(stage_name: str, meta: Optional[Dict[str, Any]] = None):
    """
    Context manager that records stage timing and telemetry.
    Integrates with Sentry spans when enabled, and emits structured log lines locally.
    """
    start_time = time.perf_counter()
    safe_meta = {k: v for k, v in (meta or {}).items() if not any(s in k.lower() for s in ["key", "secret", "token", "password", "auth"])}
    
    span = None
    if _sentry_initialized:
        try:
            import sentry_sdk
            span = sentry_sdk.start_span(op="agent.pipeline", name=stage_name)
            for k, v in safe_meta.items():
                span.set_data(k, str(v)[:100])
        except Exception:
            span = None

    try:
        yield
        duration = time.perf_counter() - start_time
        logger.info(f"[STAGE COMPLETE] {stage_name} ({duration:.3f}s) | Meta: {safe_meta}")
        if span:
            span.set_data("status", "success")
            span.set_data("duration_sec", duration)
            span.finish()
    except Exception as exc:
        duration = time.perf_counter() - start_time
        logger.error(f"[STAGE FAILED] {stage_name} ({duration:.3f}s) | Error: {type(exc).__name__}: {str(exc)}")
        if span:
            span.set_data("status", "error")
            span.set_data("error", str(exc))
            span.finish()
        if _sentry_initialized:
            try:
                import sentry_sdk
                sentry_sdk.capture_exception(exc)
            except Exception:
                pass
        raise exc
