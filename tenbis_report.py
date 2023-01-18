import re
import os
import json
import pickle
import urllib3
import requests
import appSettings
from Shovar import Shovar
from datetime import date
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CWD = os.getcwd()
FILENAME = f"report-{date.today().strftime('%d-%b-%Y')}.html"
OUTPUT_PATH = f"{CWD}/{FILENAME}"
TENBIS_FQDN = "https://www.10bis.co.il"


def main_procedure(session):
    shovarim = []
    count = 0
    years_to_check = -12
    for num in range(0, years_to_check, -1):
        month_json_result = get_report_for_month(session, str(num))
        for order in month_json_result:
            used, barcode_number, barcode_img_url, amount, valid_date = get_barcode_order_info(session,
                                                                                               order['orderId'],
                                                                                               order['restaurantId'])
            if not used:
                count += 1
                int_barcode = re.sub('\D', '', barcode_number)
                expiry = datetime.strptime(valid_date, '%d/%m/%Y').date()
                date_for_mongo = datetime(year=expiry.year, month=expiry.month, day=expiry.day)
                new_shovar = Shovar(int_barcode, int_barcode, amount, date_for_mongo, False, datetime.now(),
                                           date_for_mongo)
                shovarim.append(new_shovar)

    if count > 0:
        return shovarim
    else:
        return None


def get_report_for_month(session, month):
    endpoint = TENBIS_FQDN + "/NextApi/UserTransactionsReport"
    payload = {"culture": "he-IL", "uiCulture": "he", "dateBias": month}
    headers = {"content-type": "application/json", "user-token": session.user_token}
    response = session.post(endpoint, data=json.dumps(payload), headers=headers, verify=False)
    resp_json = json.loads(response.text)
    all_orders = resp_json['Data']['orderList']
    barcode_orders = [x for x in all_orders if x['isBarCodeOrder'] == True]

    return barcode_orders


def get_barcode_order_info(session, order_id, res_id):
    endpoint = TENBIS_FQDN + f"/NextApi/GetOrderBarcode?culture=he-IL&uiCulture=he&orderId={order_id}&resId={res_id}"
    headers = {"content-type": "application/json"}
    headers.update({'user-token': session.user_token})
    response = session.get(endpoint, headers=headers, verify=False)
    resp_json = json.loads(response.text)
    used = resp_json['Data']['Vouchers'][0]['Used']

    if not used:
        barcode_number = resp_json['Data']['Vouchers'][0]['BarCodeNumber']
        barcode_number_formatted = '-'.join(barcode_number[i:i + 4] for i in range(0, len(barcode_number), 4))
        barcode_img_url = resp_json['Data']['Vouchers'][0]['BarCodeImgUrl']
        amount = resp_json['Data']['Vouchers'][0]['Amount']
        valid_date = resp_json['Data']['Vouchers'][0]['ValidDate']
        return used, barcode_number_formatted, barcode_img_url, amount, valid_date

    return used, '', '', '', ''


def auth_tenbis():
    email = appSettings.ten_bis_mail
    endpoint = TENBIS_FQDN + "/NextApi/GetUserAuthenticationDataAndSendAuthenticationCodeToUser"
    payload = {"culture": "he-IL", "uiCulture": "he", "email": email}
    headers = {"content-type": "application/json"}
    session = requests.session()
    response = session.post(endpoint, data=json.dumps(payload), headers=headers, verify=False)
    resp_json = json.loads(response.text)

    if 200 <= response.status_code <= 210:
        return email, headers, resp_json, session
    else:
        return None


def auth_otp(email, headers, resp_json, session, otp):
    endpoint = TENBIS_FQDN + "/NextApi/GetUserV2"
    auth_token = resp_json['Data']['codeAuthenticationData']['authenticationToken']
    shop_cart_guid = resp_json['ShoppingCartGuid']
    otp = otp
    payload = {"shoppingCartGuid": shop_cart_guid,
               "culture": "he-IL",
               "uiCulture": "he",
               "email": email,
               "authenticationToken": auth_token,
               "authenticationCode": otp}
    response = session.post(endpoint, data=json.dumps(payload), headers=headers, verify=False)
    resp_json = json.loads(response.text)
    user_token = resp_json['Data']['userToken']
    session.user_token = user_token

    return session

