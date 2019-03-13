from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import DetailView

from unicef_geospatial.core.models import Upload
from .views import index, UploadWizardView, Process

urlpatterns = [
    path(r'', index, name='home'),
    path(r'login/', LoginView.as_view(template_name='login.html'), name='login'),
    path(r'logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path(r'upload/', UploadWizardView.as_view(), name='upload'),
    path(r'run/<int:pk>/', Process.as_view(), name='run'),
]
