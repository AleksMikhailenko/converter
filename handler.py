from http.server import BaseHTTPRequestHandler
from urllib.request import urlopen
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from datetime import date
import json


def process(func, url):
    response = urlopen(url)
    xml = ET.fromstring(response.read())
    return func(xml)


def parse_xml_to_dict(root):
    response = {}

    for child in list(root):
        if len(child) > 0:
            response[child.tag + '_' + child.get('ID')] = parse_xml_to_dict(child)
        else:
            response[child.tag] = child.text.strip() or ''

    return response


def get_currency_value(path):
    if not path.startswith('/api/currencies/usd?value='):
        return None

    url = 'http://cbr.ru/scripts/XML_daily.asp?date_req=' + date.today().strftime('%d.%m.%Y')
    data = process(parse_xml_to_dict, url)

    currency = {}
    try:
        value = float(urlparse(path).query.split('=')[1].replace(',', '.'))
    except ValueError as e:
        return e

    for val in data.keys():
        if data[val]['CharCode'] == 'USD':
            currency['USD'] = data[val]

    response = {
        'currency': 'USD',
        'value': value,
        'price': value * float(currency['USD']['Value'].replace(',', '.'))
    }
    return json.dumps(response)


def set_error_not_found():
    response = {
        'error': 'Not found',
        'code': 404,
        'message': 'Incorrect route inputted'
    }
    return json.dumps(response)


def set_error_bad_request():
    response = {
        'error': 'Bad request',
        'code': 400,
        'message': 'Incorrect value inputted'
    }
    return json.dumps(response)


class MyHttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        msg = get_currency_value(self.path)
        if msg is None:
            msg = set_error_not_found()
            self.send_response(404)
        elif isinstance(msg, ValueError):
            msg = set_error_bad_request()
            self.send_response(400)
        else:
            self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(msg.encode())
