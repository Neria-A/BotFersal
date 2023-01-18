from telebot import types
import random


def menu():
    markup = types.InlineKeyboardMarkup()
    barcode = (types.InlineKeyboardButton(text="שוברים", callback_data="coupon"))
    scan = (types.InlineKeyboardButton(text="סריקה", callback_data="scan"))
    close = (types.InlineKeyboardButton(text="סגירה", callback_data="close"))
    markup.row(barcode, scan)
    markup.row(close)
    return markup


def coupon_menu(result):
    markup = types.InlineKeyboardMarkup()
    two_hundred = (types.InlineKeyboardButton(text="200" + " x " + str(result.get("200")), callback_data="two_hundred"))
    hundred = (types.InlineKeyboardButton(text="100" + " x " + str(result.get("100")), callback_data="hundred"))
    fifty = (types.InlineKeyboardButton(text="50" + " x " + str(result.get("50")), callback_data="fifty"))
    forty = (types.InlineKeyboardButton(text="40" + " x " + str(result.get("40")), callback_data="forty"))
    thirty = (types.InlineKeyboardButton(text="30"  + " x " + str(result.get("30")), callback_data="thirty"))
    back = (types.InlineKeyboardButton(text="חזרה", callback_data="Back"))
    refresh = (types.InlineKeyboardButton(text="רענן שוברים", callback_data="refresh"))
    markup.row(two_hundred, hundred)
    markup.row(fifty, forty, thirty)
    markup.row(refresh)
    markup.row(back)
    return markup


def yes_or_no():
    not_used = ["😋", "🦴", "🤤", "😅", "🍽", "🤓"]
    used = ["🍔", "🌭", "🍟", "🍕", "🌮", "🥐", "🍺", "🍗", "🥩", "🥦", "🌶️", "🍑", "🍞"]
    rand_use = random.choice(used)
    rand_not_use = random.choice(not_used)
    markup = types.InlineKeyboardMarkup()
    yes = (types.InlineKeyboardButton(text= f"כן, השתמשתי {rand_use}", callback_data="Used"))
    no = (types.InlineKeyboardButton(text= f"עוד לא {rand_not_use}" , callback_data="Not Used"))
    markup.row(no, yes)
    return markup


def use_or_not(bot, call):
    bot.send_message(chat_id=call.message.chat.id,
                     text="האם השתמשת בשובר?",
                     reply_markup=yes_or_no(),
                     parse_mode='HTML')
