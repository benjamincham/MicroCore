from dynaconf import Dynaconf
from .core import MicroCore,get_service_name
from .communication import launch_api
from .monitor import OpenTelemetryWrapper
import os

def deploy_using_config(micro_core:MicroCore, yaml_filepath):
    current_env = os.environ.get('ENV', 'local')
    print(f"ENV: {current_env}")
    # Set ENV_FOR_DYNACONF based on the value of 'ENV'.
    os.environ['ENV_FOR_DYNACONF'] = current_env
    settings = Dynaconf(settings_files=[yaml_filepath],
                        environments=True,
                        default_env='local')

    config_try_launch_api(micro_core,settings)
    config_try_init_OpenTelemetryWrapper(micro_core,settings)

def config_try_init_OpenTelemetryWrapper(micro_core,settings):
    
    if settings.get("jaeger_host_name") and settings.get("jaeger_port") :
        try:
            service_name = get_service_name(micro_core)
            jaeger_host_name = settings.jaeger_host_name
            jaeger_port=int(settings.jaeger_port)
            instance=OpenTelemetryWrapper(service_name=service_name,jaeger_host_name=jaeger_host_name,jaeger_port=jaeger_port)
        except Exception as error:
            print("An exception occurred when OpenTelemetry config:", error)    
        
    
def config_try_launch_api(micro_core:MicroCore,settings):
    
    if settings.get("api_server_host")and settings.get("api_server_port") :
        try:
            api_host = settings.api_server_host
            api_port = int(settings.api_server_port)
            
            launch_api(micro_core, api_port, api_host) #create fastapi interface here
        except Exception as error:
            print("An exception occurred when launching config:", error)
            