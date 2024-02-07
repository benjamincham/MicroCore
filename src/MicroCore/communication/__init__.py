from .api import create_api
from ..monitor import OpenTelemetryWrapper
from ..core import MicroCore, get_service_name
import uvicorn



def launch_api(instance_micro_core: str, port: int = 8501, host: str = "0.0.0.0") -> None:
    opentelemetry_wrapper = OpenTelemetryWrapper(get_service_name(instance_micro_core))
    try:
        app = create_api(instance_micro_core)
        opentelemetry_wrapper.register_instrument_services("FASTAPI",app=app)
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as error:
        print("An exception occurred:", error) 