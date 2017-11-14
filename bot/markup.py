import itertools

import telegram as tel

from .db import DB
from .format import EnState, Format

class Markup:
    @classmethod
    def categories(cls):
        """
        Returns:
            tuple(title, markup)
        """
        buttons = cls._categories_buttons('')
        buttons.append([tel.InlineKeyboardButton('Back', callback_data=Format.order_menu_payload())])
        return ('Make a choiсe', tel.InlineKeyboardMarkup(buttons))

    @classmethod
    def dishes(cls, user_data):
        """
        Returns:
            tuple(title, markup)
        """
        #Instead of getting category name by a separate query, take it from the first row of the dish query and
        #put this row back by the use of iterator chaining
        category_id = Format.item_id_input(user_data)
        iterator = DB.dishes_by_category(category_id).iterator()
        item = iterator.__next__()
        buttons = []
        for item in itertools.chain(itertools.repeat(item, 1), iterator):
            payload = Format.dish_order_payload(item.id, user_data)
            buttons.append([tel.InlineKeyboardButton(cls._dish_to_str(item), callback_data=payload)])
        buttons.append([tel.InlineKeyboardButton('Back', callback_data=Format.dish_back_payload(user_data))])
        return (item.category.name, tel.InlineKeyboardMarkup(buttons))

    @classmethod
    def order_status(cls, user_data):
        """
        Returns:
            tuple(title, markup)
        """
        buttons = [[tel.InlineKeyboardButton('Confirm', callback_data=Format.order_confirm_payload(user_data))],
                   [tel.InlineKeyboardButton('Cancel', callback_data=Format.order_menu_payload())],
                   [tel.InlineKeyboardButton('More', callback_data=Format.order_more_payload(user_data))]]
        return (cls._order_to_str(user_data), tel.InlineKeyboardMarkup(buttons))

    @classmethod
    def order_more(cls, user_data):
        """
        Returns:
            tuple(title, markup)
        """
        buttons = cls._categories_buttons(user_data)
        buttons.append([tel.InlineKeyboardButton('Back', callback_data=Format.order_back_to_status_payload(user_data))])
        return (cls._order_to_str(user_data), tel.InlineKeyboardMarkup(buttons))

    @classmethod
    def order_menu(cls):
        """
        Returns:
            tuple(title, markup)
        """
        return ('Menu', cls._order_menu_markup())

    @classmethod
    def order_menu_new_prices(cls):
        """
        Returns:
            tuple(title, markup)
        """
        return ('The prices have been changed', cls._order_menu_markup())

    @classmethod
    def order_confirm(cls):
        """
        Returns:
            tuple(title, markup)
        """
        return ('Your order has been accepted', cls._order_menu_markup())

    @classmethod
    def order_list(cls, telegram_id):
        """
        Returns:
            tuple(title, markup)
        """
        def total_str():
            return '\nTotal: {}rub\nOrder dated {:%Y-%m-%d %H:%M:%S}\n'.format(cls._money_to_str(total), order_date)

        orders = DB.orders(telegram_id).dicts()
        if len(orders) == 0:
            return ('You have no orders', cls._order_menu_markup())
        str = 'Your orders:'
        order_id = orders[0]['id']
        order_date = orders[0]['order_date']
        total = 0.0
        for order in orders:
            if order_id != order['id']:
                str += total_str()
                order_id = order['id']
                order_date = order['order_date']
                total = 0.0
            quantity = order['dish_quantity']
            cost = order['dish_price']
            quantity_str = ''
            if quantity > 1:
                cost *= quantity
                quantity_str = 'x{}'.format(quantity)
            str += "\n{} ({}rub){}".format(order['name'],
                                           cls._money_to_str(order['dish_price']),
                                           quantity_str)
            total += cost
        str += total_str()
        return (str, tel.InlineKeyboardMarkup([[cls._new_order_button()], [cls._gen_prices_button()]]))

    @classmethod
    def _dish_to_str(cls, dish):
        """
        Args:
            dish (:obj:`Dish`)
        """
        return "{} ({}rub)".format(dish.name, cls._money_to_str(dish.price))

    @classmethod
    def _order_to_str(cls, user_data):
        order = ''
        total = 0.0
        for dish in DB.dishes(Format.order_input(user_data)):
            order += "\n{}".format(cls._dish_to_str(dish))
            total += dish.price
        return 'Your order is: {}\nTotal: {}rub'.format(order, cls._money_to_str(total))

    @classmethod
    def _categories_buttons(cls, user_data):
        buttons = []
        for item in DB.categories():
            buttons.append([tel.InlineKeyboardButton(item.name, callback_data=Format.category_payload(item.id, user_data))])
        return buttons

    @classmethod
    def _money_to_str(cls, n):
        return '{:,.3g}'.format(n)

    @classmethod
    def _order_menu_markup(cls):
        buttons = [[cls._new_order_button()],
                   [tel.InlineKeyboardButton('My orders', callback_data=Format.order_list_payload())],
                   [cls._gen_prices_button()]]
        return tel.InlineKeyboardMarkup(buttons)

    @classmethod
    def _new_order_button(cls):
        return tel.InlineKeyboardButton('New order', callback_data=Format.order_new_payload())

    @classmethod
    def _gen_prices_button(cls):
        return tel.InlineKeyboardButton('Generate prices', callback_data=Format.gen_prices_payload())