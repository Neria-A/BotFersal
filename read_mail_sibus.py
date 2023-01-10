import imaplib
import re
from datetime import datetime
import appSettings as appSet
import Shovar


con = imaplib.IMAP4_SSL(appSet.imap_url)

def convert_sibus_mail_to_shovar(con):
    amounts = ['30.00', '40.00', '50.00', '100.00', '200.00']

    con.select('Inbox')
    msgs = get_emails(search('FROM', appSet.sibus_email_sent_from, con), con)
    shovarim = []

    for msg in msgs:
        s = ''.join(str(x) for x in msg)

        new_string = " ".join(str(x) for x in msg)

        # looking for the barcode
        number_length = 20
        pattern = r"\D(\d{%d})\D" % number_length
        result = re.findall(pattern, s)
        bar_code = result[0]

        # find date
        cut_string = new_string.split(bar_code, 1)[1]
        date_pattern = "[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}"
        match_str = re.findall(date_pattern, cut_string)
        expiry = datetime.strptime(match_str[0], '%d/%m/%Y').date()
        date_for_mongo = datetime(year=expiry.year, month=expiry.month, day=expiry.day)

        # looking for amount
        any((amount := substring) in s for substring in amounts)

        #list of shovarim
        new_shovar = Shovar.Shovar(bar_code, bar_code, amount, date_for_mongo, False)
        shovarim.append(new_shovar)

    return shovarim


def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data


def get_emails(result_bytes, con):
    msgs = []  # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)

    return msgs