import requests
import os
import pickle
import urllib3
import json
from datetime import date
import re
import appSettings
from Shovar import Shovar
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CWD = os.getcwd()
SESSION_PATH = f"{CWD}/sessions.pickle"
TOKEN_PATH = f"{CWD}/usertoken.pickle"
FILENAME = f"report-{date.today().strftime('%d-%b-%Y')}.html"
OUTPUT_PATH = f"{CWD}/{FILENAME}"
TENBIS_FQDN = "https://www.10bis.co.il"
DEBUG = False
HTML_ROW_TEMPLATE = """
    <tr>  <td>{counter}</td>  <td>{store}</td>   <td>{order_date}</td>   <td>{barcode_number}</td>   <td style="text-align:center;"><img onclick="togglehideshow(this)" src='{barcode_img_url}'></td>   <td>{amount}</td>   <td>{valid_date}</br></br></td></tr>
    """
HTML_PAGE_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
        <script>
            function togglehideshow(element) {{
                 element.style.opacity= element.style.opacity * -1; 
            }}

            function hideall() {{
            	var elems = document.getElementsByTagName('img');
                for (var i = 0; i < elems.length; i++) {{
                    elems[i].style.opacity = -1;
                }}
            }}

            function showall() {{
            	var elems = document.getElementsByTagName('img');
                for (var i = 0; i < elems.length; i++) {{
                    elems[i].style.opacity = 1;
                }}
            }}

        </script>
        <style>
        button {{
        background-color: #43b17d; /* Green */
        border: none;
        padding: 20px;
        width: 48%;
        margin: 1%;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        cursor: pointer;
        border-radius: 12px;
      	}}
        #barcodes {{
        font-family: Arial, Helvetica, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }}

        img {{
        opacity: 1
        }}
        #barcodes td, #barcodes th {{
        border: 1px solid #ddd;
        padding: 8px;
        }}
        #barcodes tr:nth-child(even){{
        background-color: #f2f2f2;}}
        #barcodes tr:hover {{background-color: #ddd;}}
        #barcodes th {{
        padding-top: 12px;
        padding-bottom: 12px;
        vertical-align: top;
        text-align: center;
        background-color: #04AA6D;
        color: white;
        }}
        </style>
        </head>
        <body>
            <h1> Non used barcodes </h1>
            <table id="barcodes">
            <tr> <th>Item number</th> <th>Store</th>  <th>Order date</th>   <th>Barcode number</th>   <th>Barcode image</br><button onclick="showall()">Show all</button><button onclick="hideall()">Hide all</button></th>   <th>Amount</th>   <th>Expiration date</th>
            {output_table}
            </table>
        </body>
        </html>
    """


def main_procedure(session):
    create_pickle(session, SESSION_PATH)
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



def input_number(message):
    while True:
        try:
            userInput = int(input(message))
        except ValueError:
            print("Not an integer! Try again. (examples: 1,2,3,4,5)")
            continue
        else:
            return userInput
            break


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_pickle(obj, path):
    with open(path, 'wb') as session_file:
        pickle.dump(obj, session_file)


def load_pickle(path):
    with open(path, 'rb') as session_file:
        objfrompickle = pickle.load(session_file)
        return objfrompickle


def get_report_for_month(session, month):
    endpoint = TENBIS_FQDN + "/NextApi/UserTransactionsReport"
    payload = {"culture": "he-IL", "uiCulture": "he", "dateBias": month}
    headers = {"content-type": "application/json", "user-token": session.user_token}
    response = session.post(endpoint, data=json.dumps(payload), headers=headers, verify=False)

    if (DEBUG):
        print(endpoint + "\r\n" + str(response.status_code) + "\r\n" + response.text)

    resp_json = json.loads(response.text)
    all_orders = resp_json['Data']['orderList']
    barcode_orders = [x for x in all_orders if x['isBarCodeOrder'] == True]

    return barcode_orders


def get_barcode_order_info(session, order_id, res_id):
    endpoint = TENBIS_FQDN + f"/NextApi/GetOrderBarcode?culture=he-IL&uiCulture=he&orderId={order_id}&resId={res_id}"
    headers = {"content-type": "application/json"}
    headers.update({'user-token': session.user_token})
    response = session.get(endpoint, headers=headers, verify=False)
    if (DEBUG):
        print(endpoint + "\r\n" + str(response.status_code) + "\r\n" + response.text)
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
    # Phase one -> Email
    email = appSettings.ten_bis_mail
    endpoint = TENBIS_FQDN + "/NextApi/GetUserAuthenticationDataAndSendAuthenticationCodeToUser"

    payload = {"culture": "he-IL", "uiCulture": "he", "email": email}
    headers = {"content-type": "application/json"}
    session = requests.session()

    response = session.post(endpoint, data=json.dumps(payload), headers=headers, verify=False)
    resp_json = json.loads(response.text)

    if (DEBUG):
        print(endpoint + "\r\n" + str(response.status_code) + "\r\n" + response.text)

    if (200 <= response.status_code <= 210):
        return (email, headers, resp_json, session)
    else:
        return None

    # Phase two -> OTP


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
    create_pickle(user_token, TOKEN_PATH)
    session.user_token = user_token
    if (DEBUG):
        print(endpoint + "\r\n" + str(response.status_code) + "\r\n" + response.text)
        print(session)
    return session

