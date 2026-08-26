from django.contrib import admin
from store.models import Comment





from django.utils.html import format_html
from store.models import (
    Category, Product, Customer, Order, OrderItem,
    Country, City, SpecialProduct,
    ProductDiscount, CategoryDiscount, Coupon, BannerMain, VoteProduct, Invoice
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('name', 'slug')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('name', 'slug', 'price', 'discount_price', 'stock')




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_per_page = 4


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    list_filter = ('order',)
    search_fields = ('product__name',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_per_page = 4


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_per_page = 4


@admin.register(SpecialProduct)
class SpecialProductAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('product', 'special_percentage', 'quantity', 'sold', 'start_date', 'end_date')


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('product', 'percentage', 'is_active', 'start_date', 'end_date')


@admin.register(CategoryDiscount)
class CategoryDiscountAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('category', 'percentage', 'is_active', 'start_date', 'end_date')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('code', 'percentage', 'is_active', 'start_date', 'end_date', 'time_use', 'max_use')


@admin.register(BannerMain)
class BannerMainAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('id', 'title', 'is_cover', 'is_active', 'order', 'preview')
    list_editable = ('is_cover', 'is_active', 'order')
    list_filter = ('is_cover', 'is_active')
    search_fields = ('title', 'description')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.picture:
            return format_html('<img src="{}" style="height:80px; border-radius:6px"/>', obj.picture.url)
        return "—"
    preview.short_description = "Preview"



@admin.register(VoteProduct)
class VoteProductAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ['name', 'product', 'rating', 'is_publish']
    list_editable = ['is_publish']
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_publish=True)
    approve_reviews.short_description = 'Approve selected reviews'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('invoice_number', 'order', 'amount', 'status', 'created_at')
    list_editable = ('status',)




@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'is_approved', 'created_at')
    list_editable = ('is_approved',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 4
    list_display = ('user', 'phone', 'address', 'is_approved')
    list_editable = ('is_approved',)
