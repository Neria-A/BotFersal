import time
import menu
import mongo
import telebot
import tenbis_report
import generate_barcode
from Shovar import Shovar
import appSettings as appSet
from ShovarFromMongo import ShovarFromMongo

# bot init
bot = telebot.TeleBot(appSet.botToken)

# globals
message_ids = {}
barcode_ids = {}
global_shovar = []

@bot.message_handler(commands=['תפריט'])
def handle_command_adminwindow(message):
    print(f'All Users are: {appSet.user_name}')
    if message.from_user.username in appSet.user_name:
        print(f'Answering to user: {message.from_user.username}')
        bot.send_message(chat_id=message.chat.id,
                         text="BotFersal",
                         reply_markup=menu.menu(),
                         parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    local_shovar = []

    if call.data.startswith("coupon"):
        result = mongo.check_how_much_money()
        coupon_sum = mongo.coupons_sum(result)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="סה''כ כסף בשוברים: " + str(coupon_sum) + "₪",
                              message_id=call.message.message_id,
                              reply_markup=menu.coupon_menu(result),
                              parse_mode='HTML')
    if call.data.startswith("scan"):
        ten_bis_api(call)
    if call.data.startswith("two_hundred"):
        barcode = mongo.find_barcode("200")
        find_or_not(barcode, call, local_shovar, 200)
    if call.data.startswith("hundred"):
        barcode = mongo.find_barcode("100")
        find_or_not(barcode, call, local_shovar, 100)
    if call.data.startswith("fifty"):
        barcode = mongo.find_barcode("50")
        find_or_not(barcode, call, local_shovar, 50)
    if call.data.startswith("forty"):
        barcode = mongo.find_barcode("40")
        find_or_not(barcode, call, local_shovar, 40)
    if call.data.startswith("thirty"):
        barcode = mongo.find_barcode("30")
        find_or_not(barcode, call, local_shovar, 30)
    if call.data.startswith("fifteen"):
        barcode = mongo.find_barcode("15")
        find_or_not(barcode, call, local_shovar, 15)
    if call.data.startswith("Used"):
        if global_shovar[:1] != None:
            mongo.update_db(global_shovar[0])
            global_shovar.clear()
        delete_message(call, call.message.message_id)
        delete_barcode_message(call)
    if call.data.startswith("Not Used"):
        if (global_shovar[:1] != None):
            global_shovar.clear()
        delete_message(call, call.message.message_id)
        delete_barcode_message(call)
    if call.data.startswith("Back"):
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="BotFersal",
                              message_id=call.message.message_id,
                              reply_markup=menu.menu(),
                              parse_mode='HTML')
    if call.data.startswith("refresh"):
        result = mongo.check_how_much_money()
        coupon_sum = mongo.coupons_sum(result)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="סה''כ כסף בשוברים: " + str(coupon_sum) + "₪",
                              message_id=call.message.message_id,
                              reply_markup=menu.coupon_menu(result),
                              parse_mode='HTML')
    if call.data.startswith("close"):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


def find_or_not(barcode, call, local_shovar, amount):
    if None == barcode:
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f"לא קיים שובר על סך {amount}₪")
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


# TODO move to functions
def convert_mongo_to_shovar(barcode):
    shovar = ShovarFromMongo.dict_to_shovar(barcode)
    new_shovar = Shovar(shovar._id, shovar.code, shovar.amount, shovar.expiry_date, shovar.is_used, shovar.date_added,
                        shovar.date_used)
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


def ten_bis_api(call):
    sent_msg = bot.send_message(call.message.chat.id, "יש להכניס את קוד האימות שקיבלת כעת")
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
    amount = 0
    string = "מתוך השוברים שסרקתי, השוברים הבאים כבר שמורים אצלי:" + "\n"
    str_len = len(string)
    if otp.isdigit() and len(otp) == 5:
        scanning_message = bot.send_message(original_call.message.chat.id, "סורק 🧐")
        session = tenbis_report.auth_otp(email, headers, resp_json, session, otp)
        ten_bis = tenbis_report.main_procedure(session)
        for shovar in ten_bis:
            if mongo.check_if_exist(shovar.code) == None:
                count += 1
                amount += int(shovar.amount)
                mongo.insert_to_mongo(shovar.for_mongo())
            else:
                string += str(shovar.code) + "\n"
        delete_message(original_call, scanning_message.message_id)
        finish = bot.send_message(original_call.message.chat.id, "סיימתי 😁")
        time.sleep(2)
        delete_message(original_call, finish.message_id)

        if len(string) > str_len:
            temp = bot.send_message(original_call.message.chat.id, string)
            time.sleep(5)
            delete_message(original_call, temp.message_id)
        if count > 0:
            temp = bot.send_message(original_call.message.chat.id, f"נוספו {count} שוברים חדשים על סך {amount}₪")
            time.sleep(5)
            delete_message(original_call, temp.message_id)
    else:
        temp = bot.send_message(original_call.message.chat.id, "קוד לא תקין, נא ללחוץ על 'סריקה' שוב")
        time.sleep(5)
        delete_message(original_call, temp.message_id)


bot.infinity_polling()
