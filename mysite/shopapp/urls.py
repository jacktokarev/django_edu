from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("groups/", GroupsView.as_view(), name="groups"),
    path("api/", include(routers.urls)),
    
    path("products/", ProductsListView.as_view(), name="products"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/update/<int:pk>/", ProductUpdateView.as_view(), name="product_update"),
    path("products/archive/<int:pk>/", ProductDeleteView.as_view(), name="product_archive"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/latests/feed/", LatestProductsFeed(), name="products-feed"),
    
    path("orders/", OrdersListView.as_view(), name="orders"),
    path("orders/owner/<int:pk>/", OwnerOrdersListView.as_view(), name="owner_orders"),
    path("orders/<int:pk>/", OrderDetailsView.as_view(), name="order_details"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/update/<int:pk>/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/delete/<int:pk>/", OrderDeleteView.as_view(), name="order_delete"),
    # path("orders/export-data-json/", order_data_export_view, name="orders_data_export"),
    path("orders/export-data-json/", OrderDataExportView.as_view(), name="orders_data_export"),
    path("orders/owner/<int:pk>/export-data-json/", OwnerOrdersExportView.as_view(), name="owner_orders_data_export"),
]
