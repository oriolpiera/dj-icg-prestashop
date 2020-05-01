from django.contrib import admin

# Register your models here.
from .models import *

class ManufacturerAdmin(admin.ModelAdmin):
    actions = ["actualitzar_ICG", "actualitza_PS"]
    fields = ['icg_id', 'icg_name']
    list_display = ['icg_id', 'icg_name', 'ps_id', 'ps_name', 'modified_date', 'updated']
    search_fields = ['icg_id', 'icg_name', 'ps_id', 'ps_name']

    def actualitzar_ICG(self, request, queryset):
        queryset.update(icg_name = 'Canviat')

    def actualitzar_PS(self, request, queryset):
        queryset.update(icg_name = 'Canviat')

admin.site.register(Manufacturer, ManufacturerAdmin)


class ProductAdmin(admin.ModelAdmin):
    fields = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name',
        'modified_date','icg_modified_date', 'visible_web', 'manufacturer']
    list_display = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name',
        'modified_date','icg_modified_date', 'visible_web']
    search_fields = ['icg_reference', 'icg_name', 'ps_name']

#admin.site.register(Product, ProductAdmin)


class CombinationAdmin(admin.ModelAdmin):
    fields = ['ps_id','icg_talla','icg_color','product_id','ean13','discontinued']
    list_display = ['ps_id','icg_talla','icg_color','product_id','ean13','discontinued']
    search_fields = ['ps_id','icg_talla','icg_color','product_id','ean13']
    list_filter = ['discontinued', 'updated']

admin.site.register(Combination, CombinationAdmin)


class PriceAdmin(admin.ModelAdmin):
    fields = ['combination_id', 'ps_id','pvp_siva','iva','pvp']
    list_display = ['combination_id', 'ps_id','pvp_siva','iva','pvp']
    search_fields = ['combination_id', 'ps_id']

admin.site.register(Price, PriceAdmin)


class StockAdmin(admin.ModelAdmin):
    fields = ['combination_id', 'icg_stock', 'ps_stock', 'icg_modified_date']
    list_display = ['combination_id', 'icg_stock', 'ps_stock', 'icg_modified_date']
    search_fields = ['combination_id', 'icg_stock', 'ps_stock', 'icg_modified_date']

admin.site.register(Stock, StockAdmin)


class ProductOptionAdmin(admin.ModelAdmin):
    fiels = ['product_id', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name']
    list_display = ['product_id', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name']
    search_fields = ['product_id', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name']

admin.site.register(ProductOption, ProductOptionAdmin)


class ProductOptionValueAdmin(admin.ModelAdmin):
    fiels = ['po_id', 'ps_id','ps_name', 'icg_name']
    list_display = ['po_id', 'ps_id','ps_name', 'icg_name']
    search_fields = ['po_id', 'ps_id','ps_name', 'icg_name']

admin.site.register(ProductOptionValue, ProductOptionValueAdmin)


class SpecificPriceAdmin(admin.ModelAdmin):
    fiels = ['combination_id', 'ps_id','dto_percent', 'icg_modified_date']
    list_display = ['combination_id', 'ps_id','dto_percent', 'icg_modified_date']
    search_fields = ['combination_id', 'ps_id']

admin.site.register(SpecificPrice, SpecificPriceAdmin)


class ProductesPrestashop(admin.ModelAdmin):
    fields = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name',
        'modified_date','icg_modified_date', 'visible_web', 'manufacturer', 'manufacturer_name']
    readonly_fields = ['manufacturer_name', 'icg_modified_date', 'modified_date', 'icg_id',
        'icg_reference', 'icg_name']
    list_display = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name',
        'modified_date','icg_modified_date', 'visible_web', 'manufacturer_name']
    search_fields = ['icg_reference', 'icg_name', 'ps_name']
    list_filter = ['visible_web', 'updated']
    def manufacturer_name(self, instance):
        return instance.manufacturer.icg_name


admin.site.register(Product, ProductesPrestashop)
