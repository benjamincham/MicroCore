from typing import Any, Dict

from ..core import MicroCore
from ..monitor import OpenTelemetryWrapper

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse


def patch_fastapi(app: FastAPI) -> None:
    """Patch function to allow relative url resolution.

    This patch is required to make fastapi fully functional with a relative url path.
    This code snippet can be copy-pasted to any Fastapi application.
    """
    from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
    from starlette.requests import Request
    from starlette.responses import HTMLResponse

    async def redoc_ui_html(req: Request) -> HTMLResponse:
        assert app.openapi_url is not None
        redoc_ui = get_redoc_html(
            openapi_url="./" + app.openapi_url.lstrip("/"),
            title=app.title + " - Redoc UI",
        )

        return HTMLResponse(redoc_ui.body.decode("utf-8"))

    async def swagger_ui_html(req: Request) -> HTMLResponse:
        assert app.openapi_url is not None
        swagger_ui = get_swagger_ui_html(
            openapi_url="./" + app.openapi_url.lstrip("/"),
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )

        # insert request interceptor to have all request run on relativ path
        request_interceptor = (
            "requestInterceptor: (e)  => {"
            "\n\t\t\tvar url = window.location.origin + window.location.pathname"
            '\n\t\t\turl = url.substring( 0, url.lastIndexOf( "/" ) + 1);'
            "\n\t\t\turl = e.url.replace(/http(s)?:\/\/[^/]*\//i, url);"  # noqa: W605
            "\n\t\t\te.contextUrl = url"
            "\n\t\t\te.url = url"
            "\n\t\t\treturn e;}"
        )

        return HTMLResponse(
            swagger_ui.body.decode("utf-8").replace(
                "dom_id: '#swagger-ui',",
                "dom_id: '#swagger-ui',\n\t\t" + request_interceptor + ",",
            )
        )

    # remove old docs route and add our patched route
    routes_new = []
    for app_route in app.routes:
        if app_route.path == "/docs":  # type: ignore
            continue

        if app_route.path == "/redoc":  # type: ignore
            continue

        routes_new.append(app_route)

    app.router.routes = routes_new

    assert app.docs_url is not None
    app.add_route(app.docs_url, swagger_ui_html, include_in_schema=False)
    assert app.redoc_url is not None
    app.add_route(app.redoc_url, redoc_ui_html, include_in_schema=False)

    # Make graphql realtive
    from starlette import graphql

    graphql.GRAPHIQL = graphql.GRAPHIQL.replace(
        "({{REQUEST_PATH}}", '("." + {{REQUEST_PATH}}'
    )

def create_api(micro_core: MicroCore) -> FastAPI:

    opentelemetry_wrapper = OpenTelemetryWrapper()
    tracer = opentelemetry_wrapper.tracer
    predictions_counter = opentelemetry_wrapper.create_counter(name="predict_endpoint_counter", description="Count of predictions made")

    title = micro_core.name
    if "micro_core" not in micro_core.name.lower():
        title += " - micro_core"

    # TODO what about version?
    app = FastAPI(title=title, description=micro_core.description)

    patch_fastapi(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/ping", operation_id="ping",summary="Healthcheck alive",status_code=status.HTTP_200_OK)
    @app.post("/ping",operation_id="ping", summary="Healthcheck alive",status_code=status.HTTP_200_OK)
    async def ping()-> Any:  # type: ignore
        response_content = "OK"
        return response_content    
    
    @app.post(
        "/predict",
        operation_id="predict",
        response_model=micro_core.output_type,
        # response_model_exclude_unset=True,
        summary="performs prediction using the model",
        status_code=status.HTTP_200_OK,
    )
    async def predict(input: micro_core.input_type) -> Any:  # type: ignore
        with tracer.start_as_current_span("/predict") as predict_span:
            predictions_counter.add(1)
            """Executes this micro_core."""
            return micro_core(input)

    @app.get(
        "/info",
        operation_id="info",
        response_model=Dict,
        # response_model_exclude_unset=True,
        summary="Get info metadata.",
        status_code=status.HTTP_200_OK,
    )
    async def info() -> Any:  # type: ignore
        """Returns informational metadata about this micro_core."""
        return {}

    # Redirect to docs
    @app.get("/apidocs", include_in_schema=False)
    @app.get("/", include_in_schema=False)
    def root() -> Any:
        return RedirectResponse("./docs")

    return app