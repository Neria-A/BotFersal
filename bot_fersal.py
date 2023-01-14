import telebot
import appSettings as appSet
import read_mail_ten_bis
import read_mail_sibus
import imaplib
import move_mail_to_another_folder as mm
import mongo
import menu
import time
import json

import use_or_not
from ShovarFromMongo import ShovarFromMongo
from Shovar import Shovar
import generate_barcode



con = imaplib.IMAP4_SSL(appSet.imap_url, 993)
con.login(appSet.user, appSet.password)

bot = telebot.TeleBot(appSet.botToken)

message_ids = {}
global_shovar = []

def scan_mail(call):
    ten_bis = read_mail_ten_bis.convert_ten_bis_mail_to_shovar(con)
    for shovar in ten_bis:
        if(mongo.check_if_exist(shovar.code)):
            message_id = bot.send_message(call.message.chat.id, "קופון כבר קיים" + str(shovar.code)).message_id
            if call.message.chat.id in message_ids.keys():
                message_ids[call.message.chat.id].append(message_id)
            else:
                message_ids[call.message.chat.id] = [message_id]
            #alert notification
            #bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="קופון כבר קיים" + str(shovar.code))
        else:
            mongo.insert_to_mongo(shovar.for_mongo())
    sibus = read_mail_sibus.convert_sibus_mail_to_shovar(con)
    for barcode in sibus:
        if (mongo.check_if_exist(barcode.code)):
            message_id = bot.send_message(call.message.chat.id, "קופון כבר קיים" + str(barcode.code)).message_id
            if call.message.chat.id in message_ids.keys():
                message_ids[call.message.chat.id].append(message_id)
            else:
                message_ids[call.message.chat.id] = [message_id]
        else:
            mongo.insert_to_mongo(barcode.for_mongo())
    time.sleep(2)
    for message_id in message_ids[call.message.chat.id]:
        bot.delete_message(call.message.chat.id, message_id)
    ##mm.move_mail_to_another_folder(con)

@bot.message_handler(commands=['תפריט'])
def handle_command_adminwindow(message):
    bot.send_message(chat_id=message.chat.id,
                     text="תפריט ראשי",
                     reply_markup=menu.menu(),
                     parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    local_shovar = []
    if (call.data.startswith("coupon")):
        bot.edit_message_text(chat_id=call.message.chat.id,
                         text="בחר סכום",
                         message_id=call.message.message_id,
                         reply_markup=menu.coupon_menu(),
                         parse_mode='HTML')

    if (call.data.startswith("scan")):
        scan_mail(call)

    if (call.data.startswith("two_hundred")):
        barcode = mongo.find_barcode("200.00")
        find_or_not(barcode, call, local_shovar, 200)
    if (call.data.startswith("hundred")):
        barcode = mongo.find_barcode("100.00")
        find_or_not(barcode, call, local_shovar, 100)
    if (call.data.startswith("fifty")):
        barcode = mongo.find_barcode("50.00")
        find_or_not(barcode, call, local_shovar, 50)
    if (call.data.startswith("forty")):
        barcode = mongo.find_barcode("40.00")
        find_or_not(barcode, call, local_shovar, 40)
    if (call.data.startswith("thirty")):
        barcode = mongo.find_barcode("30.00")
        find_or_not(barcode, call, local_shovar, 30)

    if (call.data.startswith("Used")):
        if call.message.chat.id in message_ids.keys():
            message_ids[call.message.chat.id].append(call.message.message_id)
        else:
            message_ids[call.message.chat.id] = [call.message.message_id]
        if(global_shovar[:1] != None):
            mongo.update_db(global_shovar[0])
            global_shovar.clear()
        delete_messages(call)

    if (call.data.startswith("Not Used")):
        if call.message.chat.id in message_ids.keys():
            message_ids[call.message.chat.id].append(call.message.message_id)
        else:
            message_ids[call.message.chat.id] = [call.message.message_id]
        if (global_shovar[:1] != None):
            global_shovar.clear()
        delete_messages(call)

    if (call.data.startswith("Back")):
        bot.edit_message_text(chat_id=call.message.chat.id,
                         text="תפריט ראשי",
                         message_id=call.message.message_id,
                         reply_markup=menu.menu(),
                         parse_mode='HTML')

    if (call.data.startswith("close")):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if (call.data.startswith("check")):
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="קופון כבר קיים")

    if (call.data.startswith("how_much")):
        result = mongo.check_how_much_money()
        string = ""
        cop = " קופונים של "
        for key, value in result.items():
            string += str(value) + cop + str(key) + "\n"
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=string)


def find_or_not(barcode, call, local_shovar, amount):
    if None == barcode:
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f"לא קיים קופון על סך {amount}₪")
    else:
        local_shovar.append(convert_mongo_to_shovar(barcode))
        global_shovar.append(local_shovar[0])
        new_file = generate_barcode.generate_barcode(local_shovar[0].code)
        message_id = bot.send_photo(chat_id=call.message.chat.id, photo=new_file).message_id
        if call.message.chat.id in message_ids.keys():
            message_ids[call.message.chat.id].append(message_id)
        else:
            message_ids[call.message.chat.id] = [message_id]
        menu.use_or_not(bot, call)


#TODO move to functions
def convert_mongo_to_shovar(barcode):
    shovar = ShovarFromMongo.dict_to_shovar(barcode)
    new_shovar = Shovar(shovar._id, shovar.code, shovar.amount, shovar.expiry_date, shovar.is_used)
    return new_shovar


def delete_messages(call):
    for message_id in message_ids[call.message.chat.id]:
        bot.delete_message(call.message.chat.id, message_id)
    message_ids.clear()

def delete_message(call, message_id):
    bot.delete_message(call.message.chat.id, message_id)


bot.infinity_polling()