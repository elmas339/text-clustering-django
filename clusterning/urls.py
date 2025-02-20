from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload'),
    path('results/<int:result_id>/', views.view_results, name='results'),
]