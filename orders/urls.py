from django.urls import include,path
from django.contrib import admin
from . import views

urlpatterns=[
    path("admin",admin.site.urls),
    path("",views.index,name="index"),
    path("login",views.login,name="login"),
    path("logout",views.logout,name = "logout"),
    path("register",views.register,name = "register"),
    path("customize_pizza",views.customize_pizza,name = "customize_pizza"),
    path("add_pizza_to_cart",views.add_pizza_to_cart,name= "add_pizza_to_cart"),
    path("customize_sub",views.customize_sub,name="customize_sub"),
    path("sub_addons",views.sub_addons,name="sub_addons"),
    path("sub_sizes",views.sub_sizes,name="sub_sizes"),
    path("add_sub_to_cart",views.add_sub_to_cart,name="add_sub_to_cart"),
    path("shopping_cart",views.shopping_cart,name="shopping_cart"),
    path("shopping_cart_items",views.shopping_cart_items,name="shopping_cart_items"),
    path("add_item_to_cart",views.add_item_to_cart,name="add_item_to_cart"),
    path("remove_item_from_cart",views.remove_item_from_cart,name="remove_item_from_cart"),
    path("order",views.order,name="order"),
    path("submit_order",views.submit_order,name="submit_order"),
    path("view_orders",views.view_orders,name="view_orders"),
    path("order_history",views.order_history,name="order_history"),

    path("contact_view",views.contact_view,name="contact_view"),
    path("hours_view",views.hours_view,name="hours_view"),
]