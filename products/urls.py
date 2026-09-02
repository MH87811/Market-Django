from .views import *
from django.urls import path

app_name = 'products'

urlpatterns = [
    path('add/', AddProductView.as_view(), name='add'),
    path('list/', ProductListView.as_view(), name='list'),
    path('detail/<slug:slug>', ProductDetailView.as_view(), name='detail'),
    path('update/<slug:slug>', ProductUpdateView.as_view(), name='update'),
    path('delete/<slug:slug>', ProductDeleteView.as_view(), name='delete'),
    path('<slug:slug>/varinat/add', AddVariantView.as_view(), name='add_variant'),
    path('update/<slug:slug>/variant/<int:id>', VariantUpdateView.as_view(), name='update_variant'),
    path('delete/<slug:slug>/variant/<int:id>', VariantDeleteView.as_view(), name='delete_variant'),
]