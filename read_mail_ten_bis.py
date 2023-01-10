from datetime import datetime
import appSettings as appSet
import Shovar
import email, re



def convert_ten_bis_mail_to_shovar(con):
    amounts = ['30.00', '40.00', '50.00', '100.00']
    con.select('Inbox')
    msgs = get_emails(search('FROM', appSet.ten_bis_email_sent_from, con), con)
    shovarim = []

    for msg in msgs:
        s = ''.join(str(x) for x in msg)

        new_string = " ".join(str(x) for x in msg)

        # looking for the barcode
        number_length = 20
        pattern = r"\D(\d{%d})\D" % number_length
        result = re.findall(pattern, s)
        bar_code = " ".join(result)

        # find date
        cut_string = new_string.split(bar_code, 1)[1]
        match_str = re.search(r"\d{2}\.\d{2}\.\d{2}", cut_string)
        expiry = datetime.strptime(match_str.group(), '%d.%m.%y').date()
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