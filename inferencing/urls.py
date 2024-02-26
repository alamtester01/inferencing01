
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video/<str:filename>/', views.serve_video, name='serve_video'),
]
