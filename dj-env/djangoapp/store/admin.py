from django.contrib import admin
from .models import Brand, Product, ProductVariant, Order, OrderItem

# This allows you to add color variants directly on the Product page
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = ('name', 'brand', 'base_price')

admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(OrderItem)