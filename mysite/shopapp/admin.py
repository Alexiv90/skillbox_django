from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .command import save_csv_products,save_csv_orders
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm

class OrderItemInline(admin.TabularInline):
    extra = 0
    model = Product.orders.through


class ProductItemInline(admin.StackedInline):
    extra = 0
    model = ProductImage


@admin.action(description="Archive products")
def mark_archive(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchive(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archive,
        mark_unarchive,
        "export_csv",

    ]
    inlines = [OrderItemInline, ProductItemInline]
    list_display = "pk", "name", 'created_by', "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description", "price", "created_by"
    fieldsets = [
        (None, {"fields": ("name", "description")}),
        ("Price_options", {
            "fields": ("price", "discount"),
            "classes": ("collapse", "wide"),
        }),
        ("Images", {
            "fields": ("preview", ),
        }),
        ("Extra options", {
            "fields": ("archived", "created_by",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 50:
            return obj.description
        else:
            return obj.description[:50] + '...'

    description_short.short_description = "My Custom Field"

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "Get":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

        self.message_user(request,"Data from CSV was imported")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            )
        ]
        return new_urls + urls


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    extra = 0
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin,ExportAsCSVMixin):
    change_list_template = "shopapp/orders_changelist.html"
    actions = [
        "export_csv",
    ]
    inlines = [ProductInline]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "Get":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, 'admin/csv_form.html', context, status=400)

        save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

        self.message_user(request,"Data from CSV was imported")
        return redirect("..")


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",
            )
        ]
        return new_urls + urls