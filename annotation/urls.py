from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static

from api import settings
from .views import GetFiltersView, ProcessUserFiltersView, UploadEPPGFileView, AnnotateView


schema_view = get_schema_view(
    openapi.Info(
        title="Annotation API",
        default_version='v1',
        description="This API annotates the ePPG file on the base of PSG recordings. To test the following requests with your data (and finally annotate the file), you should follow this sequence: /filters/, /filters/selected/, /files/eppg/, /annotate/",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Optional: ReDoc UI
    path('filters/', GetFiltersView.as_view(), name='get_filters'),
    path('filters/selected/', ProcessUserFiltersView.as_view(), name='process_filters'),
    path('files/eppg/', UploadEPPGFileView.as_view(), name='upload_eppg'),
    path('annotate/', AnnotateView.as_view(), name='annotate'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)