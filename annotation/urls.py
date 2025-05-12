from django.urls import path

from . import views
from .views import GetFiltersView, ProcessUserFiltersView, UploadEPPGFileView, AnnotateView

urlpatterns = [
    path('get-filters/', GetFiltersView.as_view(), name='get_filters'),
    path('process-filters/', ProcessUserFiltersView.as_view(), name='process_filters'),
    path('upload-eppg/', UploadEPPGFileView.as_view(), name='upload_eppg'),
    path('annotate/', AnnotateView.as_view(), name='annotate'),

]