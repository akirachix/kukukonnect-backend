from django.urls import path
from . import views

urlpatterns = [
    path('publish/', views.publish_message, name='publish_message'),
    path('relay_status/', views.relay_status_api, name='relay_status_api'),
]