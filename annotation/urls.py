from django.urls import path

from . import views
from .views import GetFiltersView, ProcessUserFiltersView, UploadEPPGFileView, AnnotateView

urlpatterns = [
    path('filters/', GetFiltersView.as_view(), name='get_filters'),
    path('filters/selected/', ProcessUserFiltersView.as_view(), name='process_filters'),
    path('files/eppg/', UploadEPPGFileView.as_view(), name='upload_eppg'),
    path('annotate/', AnnotateView.as_view(), name='annotate'),

]