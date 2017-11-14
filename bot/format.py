from enum import Enum

class EnState(Enum):
    CATEGORY = 0
    DISH = 1
    ORDER_STATUS = 2
    ORDER_CONFIRM = 3
    ORDER_MORE = 4
    ORDER_LIST = 5
    ORDER_MENU = 6
    GEN_PRICES = 7

class Format:
    """
    Payload format:
    'action_id'-'selected_item_id':'ordered_dish1' 'ordered_dish2' 'ordered_dishN'
    """
    @classmethod
    def state_input(cls, str):
        return EnState(int(str.partition('-')[0]))

    @classmethod
    def item_id_input(cls, str):
        return int(str.partition('-')[2].partition(':')[0])

    @classmethod
    def order_input(cls, str):
        return str.partition(':')[2].split(' ')

    @classmethod
    def category_payload(cls, category_id, user_data):
        return "{}-{}:{}".format(EnState.DISH.value, category_id, user_data.partition(':')[2])

    @classmethod
    def dish_order_payload(cls, dish_id, user_data):
        prev_payload = user_data.partition(':')[2]
        if prev_payload == '':
            return "{}-0:{}".format(EnState.ORDER_STATUS.value, dish_id)
        return "{}-0:{} {}".format(EnState.ORDER_STATUS.value, prev_payload, dish_id)

    @classmethod
    def dish_back_payload(cls, user_data):
        if user_data.partition(':')[2]:
            return cls.order_more_payload(user_data)
        return "{}-0:".format(EnState.CATEGORY.value)

    @classmethod
    def order_confirm_payload(cls, user_data):
        return "{}-0:{}".format(EnState.ORDER_CONFIRM.value, user_data.partition(':')[2])

    @classmethod
    def order_list_payload(cls):
        return "{}".format(EnState.ORDER_LIST.value)

    @classmethod
    def order_menu_payload(cls):
        return "{}".format(EnState.ORDER_MENU.value)

    @classmethod
    def order_new_payload(cls):
        return "{}".format(EnState.CATEGORY.value)

    @classmethod
    def order_more_payload(cls, user_data):
        return "{}-0:{}".format(EnState.ORDER_MORE.value, user_data.partition(':')[2])

    @classmethod
    def order_back_to_status_payload(cls, user_data):
        return "{}-0:{}".format(EnState.ORDER_STATUS.value, user_data.partition(':')[2])

    @classmethod
    def gen_prices_payload(cls):
        return "{}".format(EnState.GEN_PRICES.value)