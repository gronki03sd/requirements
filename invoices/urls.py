from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoices_list, name='invoices-list'),
]