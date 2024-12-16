from django.contrib import admin
from .models import Product, CartItem, Cart, Order


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'created_at', 'items_display']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'contact_info']
    readonly_fields = ('total_price', 'created_at', 'phone_number', 'address')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items')

    def items_display(self, obj):
        return ", ".join([str(item.product) for item in obj.items.all()])

    items_display.short_description = 'Items'

admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)

# Register your models here.
