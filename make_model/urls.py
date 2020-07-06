from django.urls import path, include
from . import views
from .filters import ShopFilter
from django_filters.views import FilterView

urlpatterns = [
    path('', views.index),
    path('test/', views.test)

]
