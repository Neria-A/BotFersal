from telebot import types

def menu():
    markup = types.InlineKeyboardMarkup()

    barcode = (types.InlineKeyboardButton(text="קופונים", callback_data="coupon"))
    scan = (types.InlineKeyboardButton(text="סרוק", callback_data="scan"))
    how_much = (types.InlineKeyboardButton(text="כמה כסף יש לי?", callback_data="how_much"))
    close = (types.InlineKeyboardButton(text="סגור", callback_data="close"))
    markup.row(barcode, scan)
    markup.row(how_much)
    markup.row(close)
    return markup

def coupon_menu():
    markup = types.InlineKeyboardMarkup()

    two_hundred = (types.InlineKeyboardButton(text="200", callback_data="two_hundred"))
    hundred = (types.InlineKeyboardButton(text="100", callback_data="hundred"))
    fifty = (types.InlineKeyboardButton(text="50", callback_data="fifty"))
    forty = (types.InlineKeyboardButton(text="40", callback_data="forty"))
    thirty = (types.InlineKeyboardButton(text="30", callback_data="thirty"))
    back = (types.InlineKeyboardButton(text="חזור", callback_data="Back"))
    markup.row(two_hundred, hundred)
    markup.row(fifty, forty, thirty)
    markup.row(back)
    return markup

def yes_or_not():
    markup = types.InlineKeyboardMarkup()

    yes = (types.InlineKeyboardButton(text="כן, השתמשתי", callback_data="Used"))
    no = (types.InlineKeyboardButton(text="לא", callback_data="Not Used"))
    markup.row(no, yes)
    return markup

def use_or_not(bot, call):
    bot.send_message(chat_id=call.message.chat.id,
                          text="האם השתמשת בקופון?",
                          reply_markup=yes_or_not(),
                          parse_mode='HTML')