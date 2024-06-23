from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet

from .models import Product, Order
from .admin_mixins import (
    ExportAsCSVMixin,
    ImportCSVMixin,
    ImportManyCSVMixin,
)

@admin.action(description="Архивировать продукты")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, 
                  queryset: QuerySet):
    queryset.update(archived=True)

@admin.action(description="Разархивировать продукты")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, 
                  queryset: QuerySet):
    queryset.update(archived=False)

class OrderInline(admin.TabularInline):
    
    model = Product.orders.through  # orders из related_name в Order

@admin.register(Product)
class ProductAdmin(ImportCSVMixin, admin.ModelAdmin, ExportAsCSVMixin):

    change_list_template = "shopapp/products_changelist.html"    
    actions = [
        mark_archived, mark_unarchived, "export_csv", "export_related_csv",
    ]
    inlines = [
        OrderInline,
    ]
    #list_display = "pk", "name", "description", "price", "discount"
    list_display = ("pk", "name", "description_short", "price",
        "discount", "archived")  # поля для отображения на admin странице
    list_display_links = "pk", "name"  # поля - ссылки на объект
    ordering = "-name", "pk"  # поля, по котороым производится сортировка
    search_fields = "name", "description"  # поля, по которым производится поиск
    fieldsets = [
        (None, {
            "fields": ("name","description"),
        }),
        ("По цене", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Приемщик", {
            "fields": ("created_by",),
        }),
        ("Дополнительные опции", {
            "fields": ("archived",),
            "classes": ("collapse",),
            # "description": "Extra options. Field 'archived' is for soft delete",
            "description": "Дополнительные опции. Поле 'В архиве' для защищенного удаления"
        })
    ]
    
    @admin.display(description="Краткое описание")
    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


# admin.site.register(Product, ProductAdmin)  # регистрация продукта в админке 

class ProductInline(admin.StackedInline):
# class ProductInline(admin.TabularInline): # класс для отобр. связанных объектов
    
    model = Order.products.through

@admin.register(Order)
class OrderAdmin(ImportManyCSVMixin, admin.ModelAdmin, ExportAsCSVMixin):
    
    actions  = ["export_csv",]
    change_list_template = "shopapp/orders_changelist.html"
    inlines = [ # список связанных объектов
        ProductInline,  
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"
        
    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")
    
    @admin.display(description="Клиент")
    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
