import telebot
import appSettings as appSet
import read_mail_ten_bis
import read_mail_sibus
import imaplib
import move_mail_to_another_folder as mm
import mongo

con = imaplib.IMAP4_SSL(appSet.imap_url, 993)
con.login(appSet.user, appSet.password)

bot = telebot.TeleBot(appSet.botToken)

@bot.message_handler(commands=['סרוק'])
def scan_mail(message):
    ten_bis = read_mail_ten_bis.convert_ten_bis_mail_to_shovar(con)
    for shovar in ten_bis:
        mongo.insert_to_mongo(shovar.for_mongo())
    sibus = read_mail_sibus.convert_sibus_mail_to_shovar(con)
    for barcode in sibus:
        mongo.insert_to_mongo(barcode.for_mongo())
    mm.move_mail_to_another_folder(con)

bot.infinity_polling()