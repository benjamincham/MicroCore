from setuptools import setup, find_packages
import pathlib
from glob import glob
from os.path import basename, splitext
here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='MicroCore',
    
    version='0.1',

    description='Python Framework to build microservice.',

    long_description=long_description,

    long_description_content_type='text/markdown',

    classifiers=[
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    packages=find_packages(where='src', exclude=('tests', 'test', 'examples', 'docs','assets')),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    package_data={
        # If there are data files included in your packages that need to be
        # 'sample': ['package_data.dat'],
    },
    install_requires=[
        'dynaconf==3.2.1',
        'pydantic==1.8.1',
        'uvicorn==0.23.2',
        'fastapi==0.63.0',
        'starlette==0.13.6',
        'greenlet==2.0.2',
        'gevent==23.7.0',
        'numpy==1.22.4',
        'dash>=2.5.1',
        'dash-bootstrap-components>=1.1.0',
        'dash-mantine-components>=0.10.1',
        'dash-iconify>=0.1.2',
        'dash-extensions>=0.1.6',
        'kafka-python==2.0.2',
        'opentelemetry-sdk==1.19.0',
        'opentelemetry-distro==0.40b0',
        'opentelemetry-exporter-otlp-proto-grpc==1.19.0',
        'opentelemetry-instrumentation-fastapi==0.40b0',
        'opentelemetry-instrumentation-kafka-python==0.40b0',
        'opentelemetry-exporter-jaeger==1.19.0',
    ],
    setup_requires=[
        'build',
    ],
    python_requires='>=3.6',

)