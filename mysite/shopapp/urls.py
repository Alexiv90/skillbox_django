from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (ShopIndexView, ProductListView, OrderListView, OrderCreateView, GroupsListView, OrderDeleteView,
                    ProductDetailView, OrderDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
                    OrderUpdateView, ProductsDataExportView, OrdersDataExportView,ProductViewSet,OrderViewSet,LatestProductsFeed,
                    UserOrdersListView, UserOrdersDataExportView)
from django.views.decorators.cache import cache_page
app_name = 'shopapp'

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("orders", OrderViewSet)



urlpatterns = [
    # path("", cache_page(60*3)(ShopIndexView.as_view()), name="shop_index"),
    path("", ShopIndexView.as_view(), name="shop_index"),
    path("api/", include(router.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/create_product/", ProductCreateView.as_view(), name="create_product"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_archive"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),

    path("orders/", OrderListView.as_view(), name="orders_list"),
    path("orders/create_order/", OrderCreateView.as_view(), name="create_order"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("orders/export/", OrdersDataExportView.as_view(), name="orders-export"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user-orders"),
    path("users/<int:user_id>/orders/export/", UserOrdersDataExportView.as_view(), name="user-orders-export"),

    path("products/latest/feed/", LatestProductsFeed(), name="latest-products"),
]
