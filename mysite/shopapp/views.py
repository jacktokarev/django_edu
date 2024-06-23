"""Модуль объединяет представления django-приложения интернет-магазина"""
import logging
from datetime import datetime
from csv import DictWriter
from random import random
 
from django.contrib.auth.models import Group #, User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView #, FormView
from django.contrib.syndication.views import Feed
from django.core import serializers
from django.core.cache import cache

from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from shopapp.models import Product, Order
from .forms import GroupForm #, ProductForm, OrderForm
from .shopapp_mixins import ProductChangePermissionRequiredMixin, IsStaffPermissionRequiredMixin, OwnerExistsMixin
from .serializers import ProductSerializer, OrderSerializer
from .common import save_csv_items


logger = logging.getLogger(__name__)


class ShopIndexView(View):
    
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "now_time": datetime.now(),
            "products": Product.objects.filter(archived=False).all()
        }
        logger.debug("Products for shop index: %s", context["products"])
        logger.info("Rendering shop index.")
        return render(request, "shopapp/shop_index.html", context=context)


class GroupsView(View):
    
    def get(self,request: HttpRequest) -> HttpResponse:
        context = {
        "form": GroupForm(),
        "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups_list.html", context=context)
    
    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
               
        return redirect(request.path)


class LatestProductsFeed(Feed):

    title = "Shop products (latest)"
    description = "Updates on the arrival of new products in the store"
    link = reverse_lazy("shopapp:products")

    def items(self):
        return (Product.objects
            .defer("created_by")
            .filter_by(archived=False)
            .order_by("-created_at")[:10]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description


class ProductDetailsView(PermissionRequiredMixin, DetailView):
         
    permission_required = ["shopapp.view_product",]
    # model = Product
    queryset = Product.objects.prefetch_related("images").all()

    template_name = "shopapp/product_details.html"
    context_object_name = "product"


class ProductsListView(PermissionRequiredMixin, ListView):

    permission_required = ["shopapp.view_product",]
    # model = Product
    queryset = Product.objects.filter(archived=False)
    
    template_name = "shopapp/products_list.html"
    context_object_name = "products"


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для управления моделью Product.
    Полный CRUD для сущностей товара.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        # DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = [
        'name',
        "description",
    ]
    # filterset_fields = [
    #     "name",
    #     "description",
    #     "price",
    #     "discount",
    #     "archived",
    # ]
    ordering_fields = [
        "id",
        "name",
    ]

    @action(methods=["get",], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
            "created_by",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()
        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })
        return response

    @action(methods=["post"], detail=False, parser_classes=[MultiPartParser,])
    def upload_csv(self, request:Request):
        file = request.FILES["file"].file
        products = save_csv_items(file=file, encoding=request.encoding, model_type=Product)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrdersListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    permission_required = ["shopapp.view_order",]
    model = Order
    template_name = "shopapp/orders_list.html"
    context_object_name = "orders"
    
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )
class OwnerOrdersListView(LoginRequiredMixin, OwnerExistsMixin, ListView):

    model = Order
    template_name = "shopapp/owner_orders_list.html"
    context_object_name = "orders"

    queryset = (
        Order.objects
        .prefetch_related("products").defer("user")
    )

    def __init__(self, **kwargs):
        self.owner = None
        return super().__init__(**kwargs)

    def get(self, request, *args, **kwargs):
        self.set_owner(self.kwargs["pk"])
        self.queryset = self.queryset.filter(user_id=self.owner.pk)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context


class OrderViewSet(ModelViewSet):

    queryset = Order.objects.prefetch_related("products").all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = [
        "id",
        "user",
        "delivery_address",
        "promocode",
        "created_at",
        "products",
    ]
    ordering_fields = [
        "id",
        "user",
        "delivery_address",
        "created_at",
        "products",
    ]


class OrderDetailsView(PermissionRequiredMixin, DetailView):

    permission_required = ["shopapp.view_order",]
    template_name = "shopapp/order_details.html"
    
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )

 
class ProductCreateView(PermissionRequiredMixin, CreateView):
    
    permission_required = ["shopapp.add_product",]
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    template_name = "shopapp/create_product.html"
    success_url = reverse_lazy("shopapp:products")
    

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(ProductChangePermissionRequiredMixin, UpdateView):
    
    permission_required = ["shopapp.change_product",]
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    template_name = "shopapp/product_update.html"
    
    def get_success_url(self) -> str:
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk}
        )


class ProductDeleteView(ProductChangePermissionRequiredMixin, DeleteView):
    
    permission_required = ["shopapp.delete_product",]
    model = Product
    template_name = "shopapp/product_confirm_archive.html"
    success_url = reverse_lazy("shopapp:products")
    
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)
    


class OrderCreateView(PermissionRequiredMixin, CreateView):
    
    permission_required = ["shopapp.add_order",]
    model = Order
    fields = "user", "products" #, "promocode", "delivery_address"
    template_name = "shopapp/create_order.html"
    success_url = reverse_lazy("shopapp:orders")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = context["form"].fields["products"].queryset.filter(archived=False)
        context["form"].fields["products"].queryset = queryset
        return context
    

class OrderUpdateView(PermissionRequiredMixin, UpdateView):
    
    permission_required = ["shopapp.change_order",]
    model = Order
    fields = "products", "promocode", "delivery_address"
    template_name = "shopapp/order_update.html"
    
    def get_success_url(self) -> str:
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(PermissionRequiredMixin, DeleteView):
    

    permission_required = ["shopapp.delete_order",]
    model = Order
    success_url = reverse_lazy("shopapp:orders")


class OrderDataExportView(IsStaffPermissionRequiredMixin, View):
    http_method_names = ["get"]
    permission_required = []
    model = Order
    success_url = reverse_lazy("shopapp:orders")
    
 
    def get(self, request: HttpRequest) -> JsonResponse:

        orders = Order.objects.order_by("pk").select_related("user").prefetch_related("products").all()     
        orders_data = [
            {
                "id": order.pk,
                "promocode": order.promocode,
                "delivery_address": order.delivery_address,
                "user_id": order.user.id,
                "products": [product.id for product in order.products.all()],
            }
            for order in orders
        ]
        
        # тестовый фрагмент при проверке работоспособности Sentry
        # elem = orders_data[0]
        # promocode = elem["promcode"]
        # print("Promocode:", promocode)
        
        return JsonResponse({"orders": orders_data}, safe=False)


class OwnerOrdersExportView(LoginRequiredMixin, OwnerExistsMixin, View):

    http_method_names = ["get"]
    model = Order
    success_url = reverse_lazy("shopapp:orders")
    
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        owner_orders_data = cache.get(f"owner_{self.kwargs['pk']}_orders")
        if not owner_orders_data:
            self.set_owner(pk=self.kwargs["pk"])
            owner_orders_queryset = Order.objects.filter(user_id=self.owner.pk).order_by("pk").defer("user").prefetch_related("products").all()
            owner_orders_data = serializers.serialize("json", owner_orders_queryset)
            cache.set(f"owner_{self.owner.pk}_orders", owner_orders_data, 60 * 3)
        return JsonResponse({f"owner_{self.kwargs['pk']}_orders": owner_orders_data}, safe=False)


# --------------------------------------------------------------------------------------------------------

def is_staff_permission_required(user):
    return user.is_staff

@user_passes_test(is_staff_permission_required)    
def order_data_export_view(request: HttpRequest) -> JsonResponse:

    orders = Order.objects.order_by("pk").select_related("user").prefetch_related("products").all()     
    orders_data = [
        {
            "id": order.pk,
            "promocode": order.promocode,
            "delivery_address": order.delivery_address,
            "user_id": order.user.id,
            "products": [product.id for product in order.products.all()],
        }
        for order in orders
    ]
    return JsonResponse({"orders": orders_data}, safe=False)
