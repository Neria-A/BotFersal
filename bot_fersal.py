import telebot
import appSettings as appSet
import read_mail_ten_bis
import read_mail_sibus
import imaplib
import move_mail_to_another_folder as mm
import mongo
import menu


con = imaplib.IMAP4_SSL(appSet.imap_url, 993)
con.login(appSet.user, appSet.password)

bot = telebot.TeleBot(appSet.botToken)


def scan_mail(message):
    ten_bis = read_mail_ten_bis.convert_ten_bis_mail_to_shovar(con)
    for shovar in ten_bis:
        if(mongo.check_if_exist(shovar.code)):
            bot.reply_to(message, str(shovar) + "\n קופון כבר קיים")
        else:
            mongo.insert_to_mongo(shovar.for_mongo())
    sibus = read_mail_sibus.convert_sibus_mail_to_shovar(con)
    for barcode in sibus:
        if (mongo.check_if_exist(barcode.code)):
            bot.reply_to(message, str(barcode) + "\n קופון כבר קיים")
        else:
            mongo.insert_to_mongo(barcode.for_mongo())
    ##mm.move_mail_to_another_folder(con)

@bot.message_handler(commands=['תפריט'])
def handle_command_adminwindow(message):
    bot.send_message(chat_id=message.chat.id,
                     text="תפריט ראשי",
                     reply_markup=menu.menu(),
                     parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if (call.data.startswith("coupon")):
        bot.edit_message_text(chat_id=call.message.chat.id,
                         text="בחר סכום",
                         message_id=call.message.message_id,
                         reply_markup=menu.coupon_menu(),
                         parse_mode='HTML')

    if (call.data.startswith("two_hundred")):
        barcode = mongo.find_barcode("200.00")
        if None == barcode:
            bot.reply_to(call.message, "לא קיים קופון בסכום הזה")
        else:
            bot.reply_to(call.message, barcode)
    if (call.data.startswith("hundred")):
        barcode = mongo.find_barcode("100.00")
        if None == barcode:
            bot.reply_to(call.message, "לא קיים קופון בסכום הזה")
        else:
            bot.reply_to(call.message, barcode)
    if (call.data.startswith("fifty")):
        barcode = mongo.find_barcode("50.00")
        if None == barcode:
            bot.reply_to(call.message, "לא קיים קופון בסכום הזה")
        else:
            bot.reply_to(call.message, barcode)
    if (call.data.startswith("forty")):
        barcode = mongo.find_barcode("40.00")
        if None == barcode:
            bot.reply_to(call.message, "לא קיים קופון בסכום הזה")
        else:
            print(type(barcode))
            bot.reply_to(call.message, str(barcode))
    if (call.data.startswith("thirty")):
        barcode = mongo.find_barcode("30.00")
        if None == barcode:
            bot.reply_to(call.message, "לא קיים קופון בסכום הזה")
        else:
            bot.reply_to(call.message, str(barcode))


    if (call.data.startswith("Back")):
        bot.edit_message_text(chat_id=call.message.chat.id,
                         text="תפריט ראשי",
                         message_id=call.message.message_id,
                         reply_markup=menu.menu(),
                         parse_mode='HTML')

    if (call.data.startswith("close")):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


bot.infinity_polling()