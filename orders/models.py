from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from  django.core.validators import validate_comma_separated_integer_list

from jsonfield import JSONField
import json
from  decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=64,unique=True)
    customizeable = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Size(models.Model):
    name = models.CharField(max_length=64)
    price = models.PositiveIntegerField

    def __str__(self):
        return f"{self.name}"


class Item(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(
        Category,on_delete=models.CASCADE,null=True,related_name="items")
    size = models.ForeignKey(
        Size,on_delete=models.CASCADE,blank=True,null=True)
    extras_number = models.PositiveIntegerField(blank=True,null=True)
    price = models.DecimalField(
        max_digits=6,decimal_places=2,default=0,
        validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name}"


class Extra(models.Model):
    name = models.CharField(max_length=64)
    categories = models.ManyToManyField(Category,blank=True)
    items= models.ManyToManyField(Item,blank=True)
    price = models.DecimalField(
        max_digits=6,decimal_places=2,default=0,null=True,
        validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["name"]

    def get_categories(self):
        return ", ".join([str(category) for category in self.categories.all()])

    def get_items(self):
        return ", ".join([str(category) for category in self.items.all()])

    def __str__(self):
        return f"{self.name}"


class ShoppingCart(models.Model):
    username =  models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items = models.CharField(validators=[validate_comma_separated_integer_list],
                             blank=True,null=True,max_length=256)
    custom_items =  JSONField(null=True,blank=True)

    class Meta:
        verbose_name_plural = "Shopping Carts"

    def append_item(self,item_id):
        # if items list already exists, append to the list
        if self.items != None:
            items_list = self.items.split(",")
            items_list.append(item_id)

            self.items = ",".join(items_list)
        # else, add item individually
        else:
            self.items = item_id

    def append_custom_item(self,item):
        if self.custom_items == None:
            self.custom_items = []
        self.custom_items.append(item)

    def remove_item(self,item_number,item_type):
        item_number = int(item_number)
        item_index = item_number - 1

        if item_type == "static":
            items = self.get_items()
            del items[item_index]

            if items == []:
                self.items = None
            else:
                self.items = ".".join(items)
        else:
            items = self.get_custom_items()
            del items[item_index]

            if items == []:
                self.custom_items = None
            else:
                self.custom_items = items

    def get_items(self):
        if self.items ==  None:
            return []
        else:
            return self.items.split(',')

    def get_custom_items(self):
        if self.custom_items == None:
            return {}
        else:
            return self.custom_items

    def get_total_price(self):
        # get ids of items
        item_id_list = self.get_items()

        #Create array to contain items  and their properties
        item_prices = []

        #get prices of all items in shopping cart
        for item_id in item_id_list:
            #get item price
            item_price = Item.objects.get(pk=item_id).price

            #add price  to array
            item_prices.append(item_price)

        # get custom items
        custom_items = self.get_custom_items()

        # iterate through each one and add their prices to the item prices list
        for custom_item in custom_items:
            custom_item_price = custom_item["price"]
            custom_item_price = Decimal(custom_item_price)

            item_prices.append(custom_item_price)

        # add up all numbers in array for total price, round to nearest cent
        total_price = sum(item_prices)
        total_price = format(total_price,".2f")

        return total_price

    def get_quantity(self):
        items = self.items
        custom_items = self.custom_items

        if items == None  and custom_items == None:
            return 0
        elif items  and custom_items == None:
            return len(items.split(","))
        elif items == None and custom_items:
            return len(custom_items)
        else:
            return len(items.split(",")) + len(custom_items)


class Order(models.Model):
    username = models.ForeignKey(
        settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items = models.CharField(validators = [validate_comma_separated_integer_list],
                            blank=True,null=True,max_length= 256)
    custom_items = JSONField(null=True,blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True,null=True)


class OrderHistory(models.Model):
    username = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.CharField(validators=[validate_comma_separated_integer_list],
                             blank=True,null=True,max_length=256)
    custom_items = JSONField(null=True,blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        verbose_name_plural = "Order Histories"

