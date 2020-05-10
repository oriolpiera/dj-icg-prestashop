from django.contrib import admin

# Register your models here.
from .models import *
from . import prestashop

class ManufacturerAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['icg_id', 'icg_name']
    list_display = ['icg_id', 'icg_name', 'ps_id', 'ps_name', 'modified_date', 'updated']
    search_fields = ['icg_id', 'icg_name', 'ps_id', 'ps_name']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_manufacturer(obj)

admin.site.register(Manufacturer, ManufacturerAdmin)


class CombinationAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id','icg_talla','icg_color','product_id','ean13','discontinued']
    list_display = ['ps_id', 'product_id','icg_talla','icg_color','ean13','discontinued', 'created_date', 'modified_date', 'updated']
    search_fields = ['product_id__icg_reference', 'product_id__icg_name','icg_talla','icg_color','ean13']
    list_filter = ['discontinued', 'updated']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_combination(obj)

admin.site.register(Combination, CombinationAdmin)


class PriceAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id', 'combination_id', 'pvp_siva','iva','pvp']
    list_display = ['ps_id', 'combination_id','pvp_siva','iva','pvp', 'icg_modified_date',  'created_date', 'modified_date', 'updated']
    search_fields = ['combination_id__product_id__icg_reference', 'combination_id__icg_talla', 'combination_id__icg_color']
    list_filter = ['updated', 'icg_modified_date', 'iva']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_price(obj)


admin.site.register(Price, PriceAdmin)


class StockAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['ps_id', 'combination_id', 'icg_stock', 'ps_stock', 'icg_modified_date']
    list_display = ['ps_id', 'combination_id', 'icg_stock', 'ps_stock', 'icg_modified_date', 'created_date', 'modified_date']
    search_fields = ['combination_id__product_id__icg_reference', 'combination_id__icg_talla', 'combination_id__icg_color', 'icg_modified_date']
    list_filter = ['updated', 'icg_modified_date']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #TODO
            #p.tryToUpdateProduct_fromPS(obj)
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_stock(obj)

admin.site.register(Stock, StockAdmin)


class ProductOptionAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fiels = ['product_id', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name']
    list_display = ['ps_id','ps_name', 'product_id','ps_icg_type', 'ps_public_name', 'created_date', 'modified_date']
    search_fields = ['product_id__icg_reference', 'product_id__icg_name', 'ps_id','ps_name', 'ps_icg_type', 'ps_public_name']
    list_filter = ['ps_icg_type']

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #TODO
            #p.tryToUpdateProduct_fromPS(obj)
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_product_options(obj)

admin.site.register(ProductOption, ProductOptionAdmin)


class ProductOptionValueAdmin(admin.ModelAdmin):
    actions = ["baixar_de_PS", "pujar_cap_a_PS"]
    fiels = ['po_id', 'ps_id','ps_name', 'icg_name']
    list_display = ['po_id', 'ps_id','ps_name', 'icg_name', 'created_date', 'modified_date']
    search_fields = ['po_id__product_id__icg_reference', 'ps_id','ps_name', 'icg_name']
    list_filter = ['po_id__ps_icg_type']

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_product_option_value(obj)

admin.site.register(ProductOptionValue, ProductOptionValueAdmin)


class SpecificPriceAdmin(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fiels = ['ps_id', 'product_id', 'combination_id', 'dto_percent', 'icg_modified_date']
    list_display = ['ps_id', 'product_id', 'dto_percent', 'icg_modified_date', 'created_date', 'modified_date']
    search_fields = ['product_id__icg_name', 'ps_id']
    list_filter = ['updated', 'dto_percent', 'icg_modified_date']

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            #p.tryToUpdateProduct_fromPS(obj)
            #TODO
            break

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_specific_price(obj)

admin.site.register(SpecificPrice, SpecificPriceAdmin)


class ProductesPrestashop(admin.ModelAdmin):
    actions = ["baixar_de_ICG", "baixar_de_PS", "pujar_cap_a_PS"]
    fields = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name',
        'modified_date','icg_modified_date', 'visible_web', 'manufacturer', 'manufacturer_name']
    readonly_fields = ['manufacturer_name', 'icg_modified_date', 'modified_date']
    list_display = ['icg_id', 'icg_reference', 'icg_name', 'ps_id', 'ps_name',
        'visible_web', 'manufacturer_name', 'created_date', 'modified_date', 'icg_modified_date', 'updated']
    search_fields = ['icg_reference', 'icg_name', 'ps_name', 'manufacturer__icg_name']
    list_filter = ['visible_web', 'updated', 'manufacturer__icg_name']

    def manufacturer_name(self, instance):
        if instance.manufacturer:
            return instance.manufacturer.ps_name
        else:
            return 'NO_NAME'

    def baixar_de_ICG(self, request, queryset):
        for obj in queryset:
            obj.updateFromICG()

    def baixar_de_PS(self, request, queryset):
        p = prestashop.ControllerPrestashop()
        for obj in queryset:
            p.tryToUpdateProduct_fromPS(obj)

    def pujar_cap_a_PS(self, request, queryset):
        c = prestashop.ControllerPrestashop()
        for obj in queryset:
            c.get_or_create_product(obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ProductesPrestashop, self).get_readonly_fields(request, obj)
        if obj:
            return readonly_fields + ['icg_id', 'icg_name']
        return readonly_fields

admin.site.register(Product, ProductesPrestashop)
