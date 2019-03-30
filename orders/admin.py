
from django import forms
from django.contrib import admin
from .models import Category, Item, Size, Extra, ShoppingCart, Order, OrderHistory

# Register your models here.
admin.site.register(Size)
admin.site.register(Order)
admin.site.register(OrderHistory)


class CategoryForm(admin.ModelAdmin):
    list_display = ["name", "customizeable"]
    search_fields = ["name"]


admin.site.register(Category, CategoryForm)


class CustomItemChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        name = "Name: " + str(obj)
        category = "Category: " + str(obj.category)
        size = "Size: " + str(obj.size)

        item_properties_list = [name, category, size]
        item_properties_list = " | ".join(item_properties_list)

        return (item_properties_list)


class ExtraAdminForm(forms.ModelForm):
    items = CustomItemChoiceField(queryset=Item.objects.all())

    class Meta:
        model = Item
        fields = "__all__"

    # makes items form field an un-required field
    # https://stackoverflow.com/a/24045492
    def __init__(self, *args, **kwargs):
        super(ExtraAdminForm, self).__init__(*args, **kwargs)
        self.fields["items"].required = False


class ExtraAdmin(admin.ModelAdmin):
    list_display = ["name", "get_categories", "get_items", "price"]
    search_fields = ["name"]
    form = ExtraAdminForm


admin.site.register(Extra, ExtraAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "size", "extras_number", "price"]
    search_fields = ["name"]


admin.site.register(Item, ItemAdmin)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ["username"]
    search_fields = ["username"]


admin.site.register(ShoppingCart, ShoppingCartAdmin)
