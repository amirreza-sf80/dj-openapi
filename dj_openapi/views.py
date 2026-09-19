from django.shortcuts import render


def serve_swaggerui(request):
    """Start serving the Swagger UI at the given path."""
    return render(request, "dj_openapi/swagger.html")


def serve_redoc(request):
    """Start serving the ReDoc UI at the given path."""
    return render(request, "dj_openapi/redoc.html")


def serve_elements(request):
    """Start serving the OpenAPI Elements UI at the given path."""
    return render(request, "dj_openapi/elements.html")
