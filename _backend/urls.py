from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .views import NotFound

schema_view = get_schema_view(
    openapi.Info(
        title="Platform API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
handler404 = NotFound
urlpatterns = [
    path("admin/", admin.site.urls),
    # API Documentation:
    path(
        "swagger.<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # all api:
    path("api/v1/", include("api.urls")),
]
urlpatterns += static(settings.MEDIA_URL, documentation_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, documentation_root=settings.STATIC_ROOT)
