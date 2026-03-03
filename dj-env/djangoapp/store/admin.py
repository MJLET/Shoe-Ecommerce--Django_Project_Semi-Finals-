from django.contrib import admin
from .models import Brand, Product, ProductVariant, Order, OrderItem

# 🗝️ 1. GLOBAL ADMIN HEADER TEXT
admin.site.site_header = "StepUp Shoes Administration"
admin.site.site_title = "StepUp Admin Portal"
admin.site.index_title = "Inventory & Order Management"

# 🗝️ 2. THE MISSING PIECE: The Variant Inline
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    # This allows you to add Color Name, Color Code, and Image 
    # directly on the Product page

# 🗝️ 3. GLOBAL THEME OVERRIDE
class GlobalAdminStyle(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

# 🗝️ 4. UPDATED PRODUCT ADMIN (With Inlines restored)
@admin.register(Product)
class ProductAdmin(GlobalAdminStyle):
    inlines = [ProductVariantInline]
    list_display = ('name', 'brand', 'base_price')
    search_fields = ('name',)

@admin.register(Order)
class OrderAdmin(GlobalAdminStyle):
    pass

@admin.register(Brand, ProductVariant, OrderItem)
class GeneralAdmin(GlobalAdminStyle):
    pass