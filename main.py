import requests
import json


char_codes = ['USD', 'EUR', 'CNY', 'JPY']

# api link
url = "https://www.cbr-xml-daily.ru/daily_json.js"

# get data from api - convert to json
response = requests.get(url).json()

# get values by keys
# destructuring list to vars
dollar, euro, yuan, jpy = [response['Valute'][key]['Previous']
                           for key in char_codes]
# не понимаю зачем нужно делить йены на 100, 
# но без этого формула ломается
jpy /= 100

# divide 1 by valute = opposite course
exchange_valute = lambda val1, val2: \
                    round((1 / val2) / (1 / val1), 3) 
