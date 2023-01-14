import menu
import mongo

def use_or_not(bot, call, barcode):
    bot.send_message(chat_id=call.message.chat.id,
                          text="האם השתמשת בקופון?",
                          reply_markup=menu.yes_or_not(),
                          parse_mode='HTML')
    if (call.data.startswith("Used")):
        mongo.update_db(barcode)
    if (call.data.startswith("Not Used")):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="בחר סכום",
                              message_id=call.message.message_id,
                              reply_markup=menu.coupon_menu(),
                              parse_mode='HTML')