"""
В этом модуле лежат различные наборы представления по заказам и т.д.

Разные view интернет магазина
"""

import logging
from csv import DictWriter
from dataclasses import field

from django.contrib.gis.feeds import Feed
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from .command import save_csv_products
from rest_framework.parsers import MultiPartParser
from django.contrib.auth.models import Group, User
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from timeit import default_timer
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import  ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.request import Request
from .models import Product, Order, ProductImage
from .forms import ProductForm,  GroupForm
from django.views import View
from .serializers import ProductSerializer, OrderSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

log = logging.getLogger(__name__)


@extend_schema(description="Product View CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (SearchFilter,DjangoFilterBackend)
    search_fields = ('name','description')
    filterset_fields = ['name',
                        'description',
                        'price',
                        'discount',
                        'archived',
                        ]
    ordering_fields = ['name',
                        'price',
                        'discount',
                        ]

    @method_decorator(cache_page(60*2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(detail=False, methods=['GET'])
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products'
        response['Content-Disposition'] = f'attachment; filename={filename}-export.csv'
        queryset = self.filter_queryset(self.get_queryset())
        fields = ['name',
                'description',
                'price',
                'discount',
                ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow(
                {
                    field: getattr(product, field)
                    for field in fields
                }
            )
        return response

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encofing
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    @extend_schema(
        summary='Get one product by ID',
        description='Returns one product by ID',
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve( *args, **kwargs)

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (SearchFilter,DjangoFilterBackend)
    search_fields = ('name','description')
    filterset_fields = ["delivery_address",
                        "promocode",
                        "created_at",
                        "user",
                        "products",
                        ]
    ordering_fields = ['delivery_address',
                        'user',
                        'products',
                        ]

class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]

        context = {
            "time_running": default_timer(),
            "products": products,
            "Now": datetime.now(),
            "items": 5,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index")
        print(context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)
    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(request.path)


class ProductDetailView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'

class ProductListView(ListView):
    template_name = 'shopapp/products_list.html'
    queryset = Product.objects.filter(archived=False)
    context_object_name = 'products'


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "shopapp.add_product"
    model = Product
    fields = "name", "price", 'description', 'discount', 'preview'
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        self.object = self.get_object()
        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.object.created_by == self.request.user
        return has_edit_perm and created_by_current_user
    model = Product
    # fields = "name", "price", 'description', 'discount', 'preview'
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk}
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrderListView(LoginRequiredMixin, ListView):
    queryset = (Order.objects
                .select_related("user")
                .prefetch_related("products")
                )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (Order.objects
                .select_related("user")
                .prefetch_related("products")
                )

class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy("shopapp:orders_list")

class OrderUpdateView(UpdateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk}
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        elem = products_data[0]
        # name = elem["naem"]
        # print(name)
        return JsonResponse({"products": products_data})

class OrdersDataExportView(UserPassesTestMixin, View):
    def test_func(self):
        if self.request.user.is_staff:
            return True
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "product_list": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})


class LatestProductsFeed(Feed):
    title = "Products list (latest)"
    description = "Updates or change products"
    link = reverse_lazy("shopapp:products_list")
    def items(self):
        return (
            Product.objects.filter(archived__isnull=False).order_by('-created_at')[:5]
        )

    def item_title(self, item:Product):
        return item.name

    def item_description(self, item:Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, ListView):
    template_name = 'shopapp/user_order_list.html'
    model = Order
    def get_queryset(self):
        self.owner = get_object_or_404(User, id=self.kwargs["user_id"])
        queryset = Order.objects.select_related("user").filter(
        user__id = self.kwargs["user_id"]
        )
        return queryset

    def get_context_data(self, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        data["owner"] = self.owner
        return data


class UserOrdersDataExportView(LoginRequiredMixin, ListCreateAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        self.owner = get_object_or_404(User, id=self.kwargs["user_id"])
        queryset = Order.objects.select_related("user").filter(
        user__id = self.kwargs["user_id"]
        )
        return queryset

    @action(detail=False, methods=['get'])
    def get(self, request, *args, **kwargs):
        cache_key = 'user_orders_export'
        user_orders_data = cache.get(cache_key)
        if user_orders_data is None:
            data = self.get_queryset()
            serializer = self.get_serializer(data, many=True)
            cache.set(cache_key, serializer.data, 300)
            return Response(serializer.data)
        else:
            return JsonResponse({"user_orders_data": user_orders_data})
