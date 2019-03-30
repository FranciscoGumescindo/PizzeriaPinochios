# Project 3

Web Programming with Python and JavaScript

## Premise

This is an ordering site for Pinocchio's Pizza. It allows users to create an
account and login, view the menu, and submit their order.

## Additional Information

I got a bit stuck on how to store addons and toppings this time. I also didn't
stick to my schedule as well as I would have liked to. As a result, things don't
look quite as pretty as I would have hoped and there's probably a few obvious
inefficiencies that I failed to catch.

Because the project didn't turn out as well as I would have liked, I've
definitely learned a lesson in time management and proper planning with this
project. I have every intention of making my final project my best one.

## Code Snippets I Found Useful

```python
# makes items form field an un-required field
    # https://stackoverflow.com/a/24045492
    def __init__(self, *args, **kwargs):
        super(ExtraAdminForm, self).__init__(*args, **kwargs)
        self.fields["items"].required = False
```

`admin.py`

This snippet of code allowed me to make the items field of my "Extra" model,
which contains addons and toppings, to be un-required.

```javascript
// fetches csrf token
// http://musings.tinbrain.net/blog/2015/aug/28/vanilla-js-meets-djangos-csrf/
function parse_cookies() {
  var cookies = {};
  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach(function(c) {
      var m = c.trim().match(/(\w+)=(.*)/);
      if (m !== undefined) {
        cookies[m[1]] = decodeURIComponent(m[2]);
      }
    });
  }
  return cookies;
}
```

`project3.js`

I found this snippet useful for sending AJAX requests with the CSRF token.

## Superuser Credentials

Clone the `local-demo` branch to try it out on your machine.

username: `admin`
password: `pizza2018`

## File Overview

### /orders/

#### admin.py

Where I registered tables and customized how items were displayed in the admin
interface.

#### forms.py

I added first name, last name, and email fields to the user model.

#### models.py

This is where I declared each of the models for my tables. It contains models
for things such as menu items, shopping carts, toppings, and addons.

#### urls.py

This file contains paths to each of the views for the application.

#### views.py

The massive back-end workhorse of the project. This things handles login,
registration, shopping carts, order placing, and much more.

### /templates/orders/

#### customize_pizza.html and customize_sub.html

The first is a form that allows users to customize their pizza and the second is
a form that allows users to customize their sub.

#### index.html

This is where the menu items are displayed. Once where, users can add items to
their cart and navigate to the pizza and sub customization forms.

#### login.html and register.html

These complimentary files allows users to login to the site if they already
have an account and register for one if they don't. The registration form
allows users to enter their desired password twice, just in case they typed it
wrong.

#### message.html

This file is mainly used to tell users that they have successfully placed their
order.

#### order.html

This is where users are asked to confirm their purchase and can view the
contents of their shopping cart.

#### order_history.html

This is where users are able to view their past orders.

#### shopping_cart.html

This file is used to display to users what they have in their shopping cart.
It also allows them to delete items from the cart.

#### view_orders.html

This is only accessible to staff members and allows them to view all orders
that have been submitted by customers.

### /templates/orders/layouts

#### default.html

This file loads the necessary fonts, CSS, and Javascript for the site to
function. It is the base from which each of the pages is built.

### /templates/orders/includes/

#### item_tables.html

This file is responsible for displaying the contents of a user's shopping cart
or order in a tabular format.

#### message.html

This is a small snippet mainly used as a container to display information to the
user while they are on the login or registration page.

#### navbar.html

This is the main way in which users hop from page to page. It allows users to
view the menu, their cart, and their past orders. It also allows them to logout.
If Django detects that the user is a staff member, they are able to access all
of the orders via a link in the navbar.

#### order_card.html

This is used by the `view_orders` and `order_history` pages to display orders
in a tabulated form.

#### place_order_button.html

If the user is on the shopping cart page, it will redirect them to a page in
which they can confirm the contents of their order. Once on this page, the
button is used to send the order to the server and store it in the database.

#### popup-message-container.html

This is mainly used to house popup messages that tell the user that they have
successfully added an item to the cart.

#### shopping_cart_navbar.html

This bottom navigation bar allows users to see how much their order adds up to
as well as how many items they have in their cart. Clicking on the cart icon is
an alternate way to reach the shopping cart page.

### /templates/orders/handles/

#### popup-message.html

This message is displayed when the user has successfully added an item to the
cart.

#### sub-custom-addon.html

This template is mainly used to display the custom addons of the Steak and
Cheese sub.

### /static/orders/js/

#### project3.js

The front-end workhorse of the project. It mainly sends AJAX requests to the
server and displays relevant information based on those requests.

## Personal Touch

For my personal touch, I allowed users to view their past orders.
