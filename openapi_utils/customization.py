from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    # Modify the OpenAPI schema as needed
    # For example, you can change the description, tags, etc.
    openapi_schema["info"]["description"] = "This is a custom API documentation"
    return openapi_schema
