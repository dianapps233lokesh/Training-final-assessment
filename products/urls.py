from django.urls import path

from products.views import (
    CategoryListCreateAPIView,
    LowStockProductsAPIView,
    ProductListCreateAPIView,
    ProductRetrieveUpdateDestroyAPIView,
    ProductSearchAPIView,
)

urlpatterns = [
    path(
        "categories/", CategoryListCreateAPIView.as_view(), name="category-list-create"
    ),
    path("", ProductListCreateAPIView.as_view(), name="product-list-create"),
    path(
        "<int:id>/",
        ProductRetrieveUpdateDestroyAPIView.as_view(),
        name="product-detail",
    ),
    path("search/", ProductSearchAPIView.as_view(), name="product-search"),
    path("low-stock/", LowStockProductsAPIView.as_view(), name="product-low-stock"),
]
