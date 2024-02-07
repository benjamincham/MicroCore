from .service_type import communication_type, get_communication_type
from ..utils.common import singleton

from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


@singleton
class OpenTelemetryWrapper:
    def __init__(self, service_name="", jaeger_host_name:str="localhost", jaeger_port:int=6831):
        """
        Initialize the OpenTelemetryWrapper class.

        :param services: List of services to instrument. Supported: 'kafka', 'fastapi'
        """
        self.service_name = service_name
        self.instruments = {}
        self.tracer = None
        self.meter = None
        
        metrics.set_meter_provider(MeterProvider())
        self.meter = metrics.get_meter(self.service_name)

        # Register the service name
        resource = Resource(
            attributes={
                ResourceAttributes.SERVICE_NAME: self.service_name,
            }
        )

        # Initialize Tracer and Exporter
        trace.set_tracer_provider(TracerProvider(resource=resource))

        # Initialize jaeger
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host_name,
            agent_port=jaeger_port,
        )

        # Attach to BatchSpanProcessor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = trace.get_tracer(self.service_name)

    def create_counter(self, name, description="", unit="1"):
        counter = self.meter.create_counter(
            name=name,
            description=description,
            unit=unit)
        return counter

    def create_observer(self, name, description="", unit="bytes", value_type=int):
        observer = self.meter.create_observer(
            name=name,
            description=description,
            unit=unit,
            value_type=value_type,
        )
        return observer

    def register_instrument_services(self, communication_type_option, app=None):
        """
        Instrument the services based on the provided list.
        """

        service_communication_type = get_communication_type(communication_type_option)

        if service_communication_type == communication_type.KAFKA:
            KafkaInstrumentor().instrument()
        elif service_communication_type == communication_type.FASTAPI:
            if app is not None:
                FastAPIInstrumentor.instrument_app(app)
        else:
            raise ValueError(f"Unsupported service: {str(communication_type_option)}")
