from django.contrib import admin
from .models import *
from mapwidgets.widgets import GooglePointFieldWidget
from django.contrib.gis.db import models
# Register your models here.


class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'author', 'body']


# class ShopCategorytAdmin(admin.ModelAdmin):
#     list_display = ['shop', 'category']
#     search_fields = ['shop__name']


class ShopImageAdmin(admin.ModelAdmin):
    list_display = ['shop', 'img_url']
    search_fields = ['shop__name']


class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'email', 'title', 'body']

class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id','district']

class ShopAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.PointField: {"widget": GooglePointFieldWidget}
    }
    list_display = ['id', 'name','get_district' ,'location','get_category']
    search_fields = ['name']
    def get_category(self, obj):
        return "\n".join([c.category for c in obj.category.all()])
    def get_district(self, obj):
        return obj.district.district
    get_district.short_description = 'District'
    get_district.admin_order_field = 'district__district'
    


admin.site.register(Contact, ContactAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ShopImage, ShopImageAdmin)
admin.site.register(District, DistrictAdmin)