import telebot
import appSettings as appSet
import mongo
import menu
from ShovarFromMongo import ShovarFromMongo
from Shovar import Shovar
import generate_barcode
import tenbis_report
import time


bot = telebot.TeleBot(appSet.botToken)

message_ids = {}
barcode_ids = {}
global_shovar = []

def ten_bis_api(call):
    sent_msg = bot.send_message(call.message.chat.id, "הכנס SMS")
    (email, headers, resp_json, session) = tenbis_report.auth_tenbis()
    if (email, headers, resp_json, session) == None:
        time.sleep(3)
        delete_message(call, sent_msg.message_id)
        delete_message(call, sent_msg.from_user.id)
        temp = bot.send_message(call.message.chat.id, "נתונים שגויים")
        time.sleep(5)
        delete_message(call, temp.message_id)
    else:
        time.sleep(3)
        delete_message(call, sent_msg.message_id)
        bot.register_next_step_handler(sent_msg, otp_handler, email, headers, resp_json, session, call)

def otp_handler(call, email, headers, resp_json, session, original_call):
    otp = call.text
    delete_message(original_call, call.id)
    count = 0
    string = "הקופונים:" + "\n"
    str_len = len(string)
    if otp.isdigit() and len(otp) == 5:
        session = tenbis_report.auth_otp(email, headers, resp_json, session, otp)
        ten_bis = tenbis_report.main_procedure(session)
        for shovar in ten_bis:
            if mongo.check_if_exist(shovar.code) == None:
                count += 1
                mongo.insert_to_mongo(shovar.for_mongo())
            else:
                print(mongo.check_if_exist(shovar.code))
                string += str(shovar.code) + "\n"
        if len(string) > str_len:
            string += "כבר קיימים"
            temp = bot.send_message(original_call.message.chat.id, string)
            time.sleep(5)
            delete_message(original_call, temp.message_id)
        elif count > 0:
            temp = bot.send_message(original_call.message.chat.id, f"נוספו {count} חדשים")
            time.sleep(5)
            delete_message(original_call, temp.message_id)
    else:
        temp = bot.send_message(original_call.message.chat.id, "קוד לא תקין, לחץ 'סרוק' שוב")
        time.sleep(5)
        delete_message(original_call, temp.message_id)


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
        result = mongo.check_how_much_money()
        coupon_sum = mongo.coupons_sum(result)
        bot.edit_message_text(chat_id=call.message.chat.id,
                         text="סה''כ בקופונים: " + str(coupon_sum),
                         message_id=call.message.message_id,
                         reply_markup=menu.coupon_menu(result),
                         parse_mode='HTML')

    if (call.data.startswith("scan")):
        ten_bis_api(call)

    if (call.data.startswith("two_hundred")):
        barcode = mongo.find_barcode("200")
        find_or_not(barcode, call, local_shovar, 200)
    if (call.data.startswith("hundred")):
        barcode = mongo.find_barcode("100")
        find_or_not(barcode, call, local_shovar, 100)
    if (call.data.startswith("fifty")):
        barcode = mongo.find_barcode("50")
        find_or_not(barcode, call, local_shovar, 50)
    if (call.data.startswith("forty")):
        barcode = mongo.find_barcode("40")
        find_or_not(barcode, call, local_shovar, 40)
    if (call.data.startswith("thirty")):
        barcode = mongo.find_barcode("30")
        find_or_not(barcode, call, local_shovar, 30)

    if (call.data.startswith("Used")):
        if(global_shovar[:1] != None):
            mongo.update_db(global_shovar[0])
            global_shovar.clear()
        delete_message(call, call.message.message_id)
        delete_barcode_message(call)

    if (call.data.startswith("Not Used")):
        if (global_shovar[:1] != None):
            global_shovar.clear()
        delete_message(call, call.message.message_id)
        delete_barcode_message(call)

    if (call.data.startswith("Back")):
        bot.edit_message_text(chat_id=call.message.chat.id,
                         text="תפריט ראשי",
                         message_id=call.message.message_id,
                         reply_markup=menu.menu(),
                         parse_mode='HTML')

    if (call.data.startswith("refresh")):
        result = mongo.check_how_much_money()
        coupon_sum = mongo.coupons_sum(result)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="סה''כ בקופונים: " + str(coupon_sum),
                              message_id=call.message.message_id,
                              reply_markup=menu.coupon_menu(result),
                              parse_mode='HTML')

    if (call.data.startswith("close")):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)




def find_or_not(barcode, call, local_shovar, amount):
    if None == barcode:
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f"לא קיים קופון על סך {amount}₪")
    else:
        local_shovar.append(convert_mongo_to_shovar(barcode))
        global_shovar.append(local_shovar[0])
        new_file = generate_barcode.generate_barcode(local_shovar[0].code)
        message_id = bot.send_photo(chat_id=call.message.chat.id, photo=new_file).message_id
        if call.message.chat.id in barcode_ids.keys():
            barcode_ids[call.message.chat.id].append(message_id)
        else:
            barcode_ids[call.message.chat.id] = [message_id]
        menu.use_or_not(bot, call)


#TODO move to functions
def convert_mongo_to_shovar(barcode):
    shovar = ShovarFromMongo.dict_to_shovar(barcode)
    new_shovar = Shovar(shovar._id, shovar.code, shovar.amount, shovar.expiry_date, shovar.is_used, shovar.date_added, shovar.date_used)
    return new_shovar


def delete_messages(call):
    for message_id in message_ids[call.message.chat.id]:
        bot.delete_message(call.message.chat.id, message_id)
    message_ids.clear()

def delete_message(call, message_id):
    bot.delete_message(call.message.chat.id, message_id)

def delete_barcode_message(call):
    for message_id in barcode_ids[call.message.chat.id]:
        bot.delete_message(call.message.chat.id, message_id)
    barcode_ids.clear()



bot.infinity_polling()