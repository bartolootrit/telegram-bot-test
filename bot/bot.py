import telegram.ext as telx

from .config import Config
from .db import DB
from .format import EnState, Format
from .markup import Markup

class Bot:
    def __init__(self):
        self.updater = telx.Updater(Config.bot_token())
        self.updater.dispatcher.add_handler(telx.CommandHandler('menu', __class__.menu_handler))
        self.updater.dispatcher.add_handler(telx.CallbackQueryHandler(__class__.callback_handler))

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    @classmethod
    def menu_handler(cls, bot, update):
        # markup = tel.ReplyKeyboardMarkup([list(DB.menu())], resize_keyboard=True, one_time_keyboard=True)
        # bot.send_message(chat_id=update.message.chat_id, text='Make a choiсe', reply_markup=markup)
        if update.message.from_user.is_bot:
            bot.send_message(chat_id=update.message.chat_id, text="Orders from bots aren't supported")
            return
        try:
            title, markup = Markup.order_menu()
            bot.send_message(chat_id=update.message.chat_id,
                             text=title,
                             reply_markup=markup)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=update.message.chat_id, text='Error')

    @classmethod
    def callback_handler(cls, bot, update):
        callback_query = update.callback_query
        try:
            title, markup = BotStates.state_handlers[Format.state_input(callback_query.data)](update)
            bot.edit_message_text(chat_id=callback_query.message.chat_id,
                                  message_id=callback_query.message.message_id,
                                  text=title,
                                  reply_markup=markup)
        except Exception as e:
            print(e)
            cls.send_error(bot, callback_query)

    @classmethod
    def state_order_list(cls, update):
        return Markup.order_list(update.callback_query.from_user.id)

    @classmethod
    def state_category(cls, update):
        return Markup.categories()

    @classmethod
    def state_dishes(cls, update):
        return Markup.dishes(update.callback_query.data)

    @classmethod
    def state_order_status(cls, update):
        return Markup.order_status(update.callback_query.data)

    @classmethod
    def state_order_confirm(cls, update):
        q = update.callback_query
        DB.add_order(q.from_user.id, q.from_user.first_name, Format.order_input(q.data))
        return Markup.order_confirm()

    @classmethod
    def state_order_more(cls, update):
        return Markup.order_more(update.callback_query.data)

    @classmethod
    def state_order_menu(cls, update):
        return Markup.order_menu()

    @classmethod
    def state_gen_prices(cls, update):
        DB.gen_prices()
        return Markup.order_menu_new_prices()

    @classmethod
    def send_error(cls, bot, callback_query):
        bot.edit_message_text(chat_id=callback_query.message.chat_id,
                              message_id=callback_query.message.message_id,
                              text='Error')

class BotStates:
    state_handlers = {
        EnState.CATEGORY: Bot.state_category,
        EnState.DISH: Bot.state_dishes,
        EnState.ORDER_STATUS: Bot.state_order_status,
        EnState.ORDER_CONFIRM: Bot.state_order_confirm,
        EnState.ORDER_MORE: Bot.state_order_more,
        EnState.ORDER_LIST: Bot.state_order_list,
        EnState.ORDER_MENU: Bot.state_order_menu,
        EnState.GEN_PRICES: Bot.state_gen_prices
    }
