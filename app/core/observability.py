"""Application observability setup."""

import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings
from app.core.db import engine

LOG_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] "
    "[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s service=%(otelServiceName)s] "
    "%(message)s"
)
STDOUT_HANDLER_NAME = "cakf-stdout"
OTLP_HANDLER_NAME = "cakf-otlp"


class OTelContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "otelTraceID"):
            record.otelTraceID = "0"
        if not hasattr(record, "otelSpanID"):
            record.otelSpanID = "0"
        if not hasattr(record, "otelServiceName"):
            record.otelServiceName = settings.OTEL_SERVICE_NAME
        return True


class ExcludeOpenTelemetryLogsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return not record.name.startswith("opentelemetry")


def setup_observability(app: FastAPI) -> None:
    """Configure logging and OpenTelemetry exporters for the app."""
    LoggingInstrumentor().instrument(set_logging_format=False)
    _configure_root_logger()

    tracer_provider: TracerProvider | None = None
    logger_provider: LoggerProvider | None = None

    if settings.OTEL_ENABLED:
        resource = Resource.create(
            {
                "service.name": settings.OTEL_SERVICE_NAME,
                "service.version": settings.VERSION,
            }
        )

        if settings.OTEL_TRACES_ENABLED:
            tracer_provider = TracerProvider(resource=resource)
            tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint=_resolve_signal_endpoint(
                            settings.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
                            "v1/traces",
                        )
                    )
                )
            )
            trace.set_tracer_provider(tracer_provider)
            FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
            SQLAlchemyInstrumentor().instrument(
                engine=engine.sync_engine,
                tracer_provider=tracer_provider,
            )

        if settings.OTEL_LOGS_ENABLED:
            logger_provider = LoggerProvider(resource=resource)
            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(
                    OTLPLogExporter(
                        endpoint=_resolve_signal_endpoint(
                            settings.OTEL_EXPORTER_OTLP_LOGS_ENDPOINT,
                            "v1/logs",
                        )
                    )
                )
            )
            _set_otlp_handler(logger_provider)
        else:
            _remove_handler(OTLP_HANDLER_NAME)
    else:
        _remove_handler(OTLP_HANDLER_NAME)

    if tracer_provider is not None or logger_provider is not None:
        app.router.on_shutdown.append(
            _build_shutdown_handler(tracer_provider, logger_provider)
        )

    logging.getLogger(__name__).info(
        "Observability configured stdout=%s otel=%s traces=%s logs=%s",
        settings.LOG_STDOUT_ENABLED,
        settings.OTEL_ENABLED,
        settings.OTEL_ENABLED and settings.OTEL_TRACES_ENABLED,
        settings.OTEL_ENABLED and settings.OTEL_LOGS_ENABLED,
    )


def _build_shutdown_handler(
    tracer_provider: TracerProvider | None,
    logger_provider: LoggerProvider | None,
):
    def shutdown() -> None:
        if tracer_provider is not None:
            tracer_provider.shutdown()
        if logger_provider is not None:
            logger_provider.shutdown()

    return shutdown


def _configure_root_logger() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(_parse_log_level(settings.LOG_LEVEL))

    if settings.LOG_STDOUT_ENABLED:
        stdout_handler = _get_handler(STDOUT_HANDLER_NAME)
        if stdout_handler is None:
            stdout_handler = logging.StreamHandler()
            stdout_handler.set_name(STDOUT_HANDLER_NAME)
            stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
            stdout_handler.addFilter(OTelContextFilter())
            root_logger.addHandler(stdout_handler)
    else:
        _remove_handler(STDOUT_HANDLER_NAME)


def _set_otlp_handler(logger_provider: LoggerProvider) -> None:
    root_logger = logging.getLogger()
    otlp_handler = _get_handler(OTLP_HANDLER_NAME)
    if otlp_handler is not None:
        root_logger.removeHandler(otlp_handler)

    otlp_handler = LoggingHandler(logger_provider=logger_provider)
    otlp_handler.set_name(OTLP_HANDLER_NAME)
    otlp_handler.addFilter(OTelContextFilter())
    otlp_handler.addFilter(ExcludeOpenTelemetryLogsFilter())
    root_logger.addHandler(otlp_handler)


def _get_handler(handler_name: str) -> logging.Handler | None:
    for handler in logging.getLogger().handlers:
        if handler.get_name() == handler_name:
            return handler
    return None


def _remove_handler(handler_name: str) -> None:
    handler = _get_handler(handler_name)
    if handler is not None:
        logging.getLogger().removeHandler(handler)


def _parse_log_level(level_name: str) -> int:
    return getattr(logging, level_name.upper(), logging.INFO)


def _resolve_signal_endpoint(signal_endpoint: str, signal_path: str) -> str:
    if signal_endpoint:
        return signal_endpoint
    return f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT.rstrip('/')}/{signal_path}"
