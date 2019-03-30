from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as logout_request
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from .models import Category, Item, ShoppingCart, Extra, Order, OrderHistory

from decimal import Decimal

import json
import operator

# Create your views here.


def index(request):
    # check to see if user is logged in, redirect to login if not
    if not request.user.is_authenticated:
        return redirect("login")
    # gets total price of items in cart
    total_price = get_total_price(request)

    context = {
        "categories": Category.objects.all(),
        "items": Item.objects.all(),
        "total_price": total_price
    }
    return render(request, "orders/index.html", context)


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "orders/login.html",
                          {"message": "Invalid credentials."})

    if request.user.is_authenticated:
        return redirect("index")
    else:
        return render(request, "orders/login.html")


def register(request):
    if request.method == "POST":
        # capture form inputs
        first_name = request.POST["first-name"]
        last_name = request.POST["last-name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm-password"]

        # Capitalize first and last name
        first_name.capitalize()
        last_name.capitalize()

        # if passwords match, proceed; else, inform the user
        if password == confirm_password:
            # if the username is already taken, inform the user
            if User.objects.filter(username=username).exists():
                return render(request, "orders/register.html",
                              {"message": "Username already taken."})
            # if the password is too short, inform the user
            if len(password) < 8:
                return render(request, "orders/register.html",
                              {"message": "Passwords must be at least 8 \
                               characters in length."})
            # register user
            user = User.objects.create_user(
                username=username, first_name=first_name, last_name=last_name,
                email=email, password=password)
            user.save()

            # redirect user to login page, display success message
            return render(request, "orders/login.html",
                          {"message": "Successfully registered. Please login."})
        else:
            return render(request, "orders/register.html",
                          {"message": "Passwords don't match."})

    if request.user.is_authenticated:
        return redirect("index")
    else:
        return render(request, "orders/register.html")


def logout(request):
    logout_request(request)

    return render(request, "orders/login.html", {"message": "Logged out."})


def customize_pizza(request):
    # for post requests, fetch the price of the customized pizza
    if request.method == "POST":
        data = json.loads(request.body)

        # fetch pizza item in database
        pizza_object = fetch_pizza_item(data)

        # fetch the price of the pizza
        pizza_price = pizza_object.price

        return JsonResponse({"pizza_price": pizza_price})
    # for get requests, generate the pizza customization form
    else:
        # find all categories with the word "Pizza"
        pizza_categories = Category.objects.filter(
            name__icontains="Pizza").values("name")

        # turn the QuerySet into a list while stripping the dict keys
        pizza_categories = [pizza_category["name"]
                            for pizza_category in pizza_categories]

        # fetch all extras and turn the QuerySet into a list
        extras = Extra.objects.all()
        list(extras)

        # set array in anticipation for toppings
        toppings = []

        # fetch toppings from extras
        for extra in extras:
            if "Pizza" in extra.get_categories():
                topping = extra.name
                toppings.append(topping)

        # get price of cart
        total_price = get_total_price(request)

        context = {
            "pizza_categories": pizza_categories,
            "toppings": toppings,
            "total_price": total_price
        }

        return render(request, "orders/customize_pizza.html", context)


def add_pizza_to_cart(request):
    if request.method == "POST":
        # fetch user submitting the pizza
        current_user = request.user

        # capture ajax data
        data = json.loads(request.body)

        # fetch pizza item in database
        pizza_object = fetch_pizza_item(data)

        # capture toppings of the customized pizza
        pizza_toppings = data["pizza_toppings"]

        # create dict to store pizza properties
        pizza = {}

        # add pizza properties to dict
        pizza["name"] = str(pizza_object.name)
        pizza["category"] = str(pizza_object.category)
        pizza["size"] = str(pizza_object.size)
        pizza["price"] = "{0:.2f}".format(pizza_object.price)
        pizza["pizza_toppings"] = pizza_toppings

        # fetch shopping cart of the current user
        shopping_cart = fetch_shopping_cart(current_user)

        # add the pizza to the custom items section of the cart
        shopping_cart.append_custom_item(pizza)
        shopping_cart.save()

        # fetch the quantity and total price of items in the cart
        quantity = get_quantity(request)
        total_price = get_total_price(request)

        return JsonResponse({"quantity": quantity,
                             "total_price": total_price})
    else:
        return HttpResponseForbidden()


def customize_sub(request):
    # for posts requests, fetch the price of the customized sub
    if request.method == "POST":
        # fetch current user
        current_user = request.user

        # capture ajax request data
        data = json.loads(request.body)

        # fetch sub item in database
        sub_object = fetch_sub_item(data)

        # fetch the price of the sub
        sub_price = sub_object.price

        # fetch the sub addons
        sub_addons = data["sub_addons"]

        # create dict to store sub properties
        sub = {}

        # add sub properties to dict
        sub["name"] = str(sub_object.name)
        sub["category"] = str(sub_object.category)
        sub["size"] = str(sub_object.size)
        sub["price"] = "{0:.2f}".format(sub_object.price)
        sub["sub_addons"] = sub_addons

        # create list to capture prices of addons
        addon_total = []

        # fetch all extras and turn the QuerySet into a list
        extras = Extra.objects.all()
        list(extras)

        # fetch the prices of the sub's custom addons
        for extra in extras:
            for sub_addon in sub_addons:
                if (sub_addon in extra.name):
                    addon_price = Decimal(extra.price)
                    addon_total.append(addon_price)

        # add the prices of the addons together and add them to sub's base price
        addon_total = sum(addon_total)
        sub_price = sub_price + addon_total

        return JsonResponse({"sub_price": sub_price})

    # for get requests, generate the sub customization form
    else:
        # get current user
        current_user = request.user

        # find all subs on in the item database
        sub_names = Item.objects.filter(category__name="Subs").values("name")

        # turn the QuerySet into a list while stripping the dict keys
        sub_names = [sub_name["name"] for sub_name in sub_names]

        # remove duplicate names from the list and order alphabetically
        sub_names = set(sub_names)
        sub_names = sorted(sub_names)

        # fetch all extras and turn the QuerySet into a list
        extras = Extra.objects.all()
        list(extras)

        # set array in anticipation for addons
        addons = []

        # fetch addons from extras
        for extra in extras:
            if "Subs" in extra.get_categories():
                addon = extra.name
                addons.append(addon)

        # get quantity and total price of items in shopping cart
        quantity = get_quantity(request)
        total_price = get_total_price(request)

        context = {
            "sub_names": sub_names,
            "addons": addons,
            "quantity": quantity,
            "total_price": total_price
        }

        return render(request, "orders/customize_sub.html", context)


def sub_addons(request):
    if request.method == "POST":
        # capture ajax request data
        data = json.loads(request.body)

        # fetch the name of the sub
        sub_name = data["sub_name"]

        # fetch all extras and turn the QuerySet into a list
        extras = Extra.objects.all()
        list(extras)

        # set list in anticipation for fetching sub addons
        addons = []

        # fetch generic and custom addons
        for extra in extras:
            # find generic addons
            if "Subs" in extra.get_categories():
                addon = extra.name
                addons.append(addon)

            # take items output, make it into a list, and remove dupes done in
            # preparation for finding custom addons
            items = extra.get_items().split(", ")
            items = list(items)
            items = set(items)

            # find custom addons
            if sub_name in items:
                addon = extra.name
                addons.append(addon)

        return JsonResponse({"sub_addons": addons})
    else:
        return HttpResponseForbidden()


def sub_sizes(request):
    if request.method == "POST":
        # capture ajax request data
        data = json.loads(request.body)

        # extract sub name
        sub_name = data["sub_name"]

        # fetch sub with corresponding name
        sub_object = Item.objects.filter(name=sub_name).first()

        # see if size value for the sub exists
        if (sub_object.size):
            sub_sizes = True
        else:
            sub_sizes = False

        return JsonResponse({"sub_sizes": sub_sizes})


def add_sub_to_cart(request):
    if request.method == "POST":
        # fetch user submitting the pizza
        current_user = request.user

        # capture ajax data
        data = json.loads(request.body)

        # fetch sub item in database
        sub_object = fetch_sub_item(data)

        # capture toppings of the customized pizza
        sub_addons = data["sub_addons"]

        # create dict to store sub properties
        sub = {}

        # add sub properties to dict
        sub["name"] = str(sub_object.name)
        sub["category"] = str(sub_object.category)
        sub["size"] = str(sub_object.size)
        sub["price"] = "{0:.2f}".format(sub_object.price)
        sub["sub_addons"] = sub_addons

        # fetch all extras and turn the QuerySet into a list
        extras = Extra.objects.all()
        list(extras)

        # fetch addons from extras and factor in their price to the sub's total
        for extra in extras:
            for sub_addon in sub_addons:
                if sub_addon in extra.name:
                    price = Decimal(sub["price"])
                    price = price + extra.price
                    sub["price"] = "{0:.2f}".format(price)

        # fetch shopping cart of the current user
        shopping_cart = fetch_shopping_cart(current_user)

        # add the sub to the custom items section of the cart
        shopping_cart.append_custom_item(sub)
        shopping_cart.save()

        # fetch the quantity and total price of items in the cart
        quantity = get_quantity(request)
        total_price = get_total_price(request)

        return JsonResponse({"quantity": quantity,
                             "total_price": total_price})
    else:
        return HttpResponseForbidden()


def shopping_cart(request):
    if request.method == "POST":
        return True
    else:
        # check to see if user is logged in, redirect to login if not
        if not request.user.is_authenticated:
            return redirect("login")

        # find total price of items in shopping cart
        total_price = get_total_price(request)

        # fetch current user
        current_user = request.user

        # fetch user's shopping cart
        shopping_cart = fetch_shopping_cart(current_user)

        # get all of the item ids in the cart
        item_id_list = shopping_cart.get_items()

        # create array to contain items and their properties
        items = []

        # get properties of all items in the cart and add them to a list
        for item_id in item_id_list:
            # create dict to store item properties in
            item_dict = {}

            # get item properties
            item = Item.objects.get(pk=item_id)

            # add properties to item dict
            item_dict["id"] = item.id
            item_dict["name"] = item.name
            item_dict["category"] = str(item.category)
            item_dict["size"] = str(item.size)
            item_dict["price"] = str(item.price)

            # add item dict to items array
            items.append(item_dict)

        # sort items by name
        items.sort(key=operator.itemgetter("name"))

        # get all of the custom items in the cart
        custom_items = shopping_cart.get_custom_items()

        context = {
            "items": items,
            "custom_items": custom_items,
            "total_price": total_price
        }

        return render(request, "orders/shopping_cart.html", context)


def shopping_cart_items(request):
    if request.method == "POST":
        # capture user requesting information
        current_user = request.user

        #  fetch quantity and total price of cart
        quantity = get_quantity(request)
        total_price = get_total_price(request)

        # return shopping cart quantity
        return JsonResponse({"quantity": quantity,
                             "total_price": total_price})
    else:
        return HttpResponseForbidden()


def add_item_to_cart(request):
    # capture user requesting information
    current_user = request.user

    # load json from ajax request
    data = json.loads(request.body)

    # if item_id exists, run protocol for adding item to cart
    if "item_id" in data:
        # capture item
        item_id = data["item_id"]

        # fetch the user's shopping cart or create it if it doesn't exist
        shopping_cart = fetch_shopping_cart(current_user)

        # call function to add item and save it
        shopping_cart.append_item(item_id)
        shopping_cart.save()

        # get quantity and total price of items in cart
        quantity = get_quantity(request)
        total_price = get_total_price(request)

        return JsonResponse({"quantity": quantity,
                             "total_price": total_price})


def remove_item_from_cart(request):
    # capture current user
    current_user = request.user

    # load json from ajax request
    data = json.loads(request.body)

    # capture item number
    item_number = data["item_number"]
    item_type = data["item_type"]

    # fetch the user's shopping cart
    shopping_cart = fetch_shopping_cart(current_user)

    # call function to remove item
    shopping_cart.remove_item(item_number, item_type)
    shopping_cart.save()

    return JsonResponse({"success": True})


def order(request):
    # check to see if user is logged in, redirect to login if not
    if not request.user.is_authenticated:
        return redirect("login")

    # get current user
    current_user = request.user

    # get user's cart
    shopping_cart = fetch_shopping_cart(current_user)

    # if the cart is empty, redirect user to main page
    if (shopping_cart.items == None) and (shopping_cart.custom_items == None):
        return render(request, "orders/message.html",
                      {"title": "Error!",
                       "message": "Cart empty! Please make a selection before \
                       proceeding."})
    else:
        # find total price of items in shopping cart
        total_price = get_total_price(request)

        # get all of the item ids in the cart
        item_id_list = shopping_cart.get_items()

        # create array to contain items and their properties
        items = []

        # get properties of all items in the cart and add them to a list
        for item_id in item_id_list:
            # create dict to store item properties in
            item_dict = {}

            # get item properties
            item = Item.objects.get(pk=item_id)

            # add properties to item dict
            item_dict["id"] = item.id
            item_dict["name"] = item.name
            item_dict["category"] = str(item.category)
            item_dict["size"] = str(item.size)
            item_dict["price"] = str(item.price)

            # add item dict to items array
            items.append(item_dict)

        # sort items by name
        items.sort(key=operator.itemgetter("name"))

        # get all of the custom items in the cart
        custom_items = shopping_cart.get_custom_items()

        context = {
            "items": items,
            "custom_items": custom_items,
            "total_price": total_price
        }

    return render(request, "orders/order.html", context)


def submit_order(request):
    # get current user
    current_user = request.user

    # get user's cart
    shopping_cart = fetch_shopping_cart(current_user)

    # copy shopping cart contents to orders and order history
    order = Order.objects.create(
        username=current_user, items=shopping_cart.items,
        custom_items=shopping_cart.custom_items)
    order.save()

    order = OrderHistory.objects.create(
        username=current_user, items=shopping_cart.items,
        custom_items=shopping_cart.custom_items)
    order.save()

    # destroy shopping cart item
    shopping_cart.delete()

    return render(request, "orders/message.html",
                  {"title": "Success!",
                   "message": "Order has been placed! Thanks for choose 'Nochs!"})


@user_passes_test(lambda u: u.is_staff, login_url=('login'))
def view_orders(request):
    # fetch all orders
    order_objects = Order.objects.all()

    # create list to insert orders into
    orders = []

    # fetch information of static items; extract properties of each order, put
    # them in a dict, and add them to the list
    for order_object in order_objects:

        # if order has static item objects
        if order_object.items != None:
            # get all of the item ids in the cart
            item_id_list = order_object.items
            item_id_list = item_id_list.split(",")

            # create array to contain items and their properties
            items = []

            # get properties of all items in the cart and add them to a list
            for item_id in item_id_list:
                # create dict to store item properties in
                item_dict = {}

                # get item properties
                item = Item.objects.get(pk=item_id)

                # add properties to item dict
                item_dict["id"] = item.id
                item_dict["name"] = item.name
                item_dict["category"] = str(item.category)
                item_dict["size"] = str(item.size)
                item_dict["price"] = str(item.price)

                # add item dict to items array
                items.append(item_dict)

            # sort items by name
            items.sort(key=operator.itemgetter("name"))
        else:
            items = None

        # create dict to store order properties in
        order = {}

        # extract order properties
        order["username"] = order_object.username
        order["items"] = items
        order["custom_items"] = order_object.custom_items
        order["submitted_at"] = order_object.submitted_at.strftime(
            "%Y-%m-%d %I:%M:%S %p")

        # add order dict to the orders list
        orders.append(order)

    context = {
        "orders": orders
    }

    return render(request, "orders/view_orders.html", context)


def order_history(request):
    # check to see if user is logged in
    if not request.user.is_authenticated:
        return redirect("login")

    # get current user
    current_user = request.user

    # fetch orders with the user's name
    order_objects = OrderHistory.objects.filter(username=current_user)

    # create list to insert orders into
    orders = []

    # fetch information of static items; extract properties of each order, put
    # them in a dict, and add them to the list
    for order_object in order_objects:

        # if order has static item objects
        if order_object.items != None:
            # get all of the item ids in the cart
            item_id_list = order_object.items
            item_id_list = item_id_list.split(",")

            # create array to contain items and their properties
            items = []

            # get properties of all items in the cart and add them to a list
            for item_id in item_id_list:
                # create dict to store item properties in
                item_dict = {}

                # get item properties
                item = Item.objects.get(pk=item_id)

                # add properties to item dict
                item_dict["id"] = item.id
                item_dict["name"] = item.name
                item_dict["category"] = str(item.category)
                item_dict["size"] = str(item.size)
                item_dict["price"] = str(item.price)

                # add item dict to items array
                items.append(item_dict)

            # sort items by name
            items.sort(key=operator.itemgetter("name"))
        else:
            items = None

        # create dict to store order properties in
        order = {}

        # extract order properties
        order["username"] = order_object.username
        order["items"] = items
        order["custom_items"] = order_object.custom_items
        order["submitted_at"] = order_object.submitted_at.strftime(
            "%Y-%m-%d %I:%M:%S %p")

        # add order dict to the orders list
        orders.append(order)

    context = {
        "orders": orders
    }

    return render(request, "orders/order_history.html", context)

####################
# helper functions #
####################

def get_total_price(request):
    # get current user
    current_user = request.user

    # if a shopping cart for the user exists, get total price of cart
    if ShoppingCart.objects.filter(username=current_user):
        shopping_cart = ShoppingCart.objects.get(username=current_user)
        total_price = shopping_cart.get_total_price()
    # else return a default value
    else:
        total_price = "0.00"

    return total_price


def fetch_pizza_item(data):
    # fetch pizza properties
    pizza_category = data["pizza_category"]
    pizza_size = data["pizza_size"]
    pizza_toppings = data["pizza_toppings"]

    # get number of toppings
    pizza_toppings_number = len(pizza_toppings)

    # if there are greater than 4 toppings, treat it as a 4 topping pizza
    if pizza_toppings_number > 4:
        pizza_extras_number = 4
    # else, treat it as normal
    else:
        pizza_extras_number = pizza_toppings_number

    # sort to find the correct item entry for the pizza
    pizza_object = Item.objects.filter(
        category__name__contains=pizza_category).filter(
        size__name__contains=pizza_size).get(
        extras_number=pizza_extras_number)

    return pizza_object


def fetch_sub_item(data):
    # fetch sub properties
    sub_name = data["sub_name"]
    sub_size = data["sub_size"]

    # sort to find items that match the name of the sub
    sub_object = Item.objects.filter(name=sub_name)

    # if the item has an entry with corresponding size, fetch it
    if (sub_object.filter(size__name__contains=sub_size).exists()):
        sub_object = sub_object.get(size__name__contains=sub_size)
    # else, just fetch the object by name
    else:
        sub_object = Item.objects.get(name=sub_name)

    return sub_object


def fetch_shopping_cart(current_user):
    # if a cart exists for the user, find it
    if ShoppingCart.objects.filter(username=current_user):
        shopping_cart = ShoppingCart.objects.get(username=current_user)
    # if not, create cart
    else:
        shopping_cart = ShoppingCart.objects.create(
            username=current_user)

    return shopping_cart


def get_quantity(request):
    # get current user
    current_user = request.user

    # if shopping cart exists for the user, return quantity, else return
    # default value of 0
    if ShoppingCart.objects.filter(username=current_user):
        shopping_cart = ShoppingCart.objects.get(username=current_user)

        # get shopping cart quantity
        quantity = shopping_cart.get_quantity()

        # return shopping cart quantity
        return quantity
    else:
        return 0


def contact_view(request):
    return render(request,'orders/contact.html')


def hours_view(request):
    return render(request,'orders/hours.html')