"""
URLs do app reserveme.
"""
from django.urls import path
from reserveme.views.example_views import (
    example_list_create,
    example_detail,
)

app_name = 'reserveme'

urlpatterns = [
    path('examples/', example_list_create, name='example-list-create'),
    path('examples/<int:pk>/', example_detail, name='example-detail'),
]
