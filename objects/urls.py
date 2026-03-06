from django.urls import path
from . import views

app_name = "objects"

urlpatterns = [
    path('', views.map_view, name='map'),
    path('api/markers/', views.api_markers, name='api_markers'),
    path('api/filters/', views.api_filters, name='api_filters'),
]
