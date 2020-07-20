import requests
import json
from db import db, db_session, Valutes

# ---PURE SECTION---
char_codes = ['USD', 'EUR', 'CNY', 'JPY']

# api link
url = "https://www.cbr-xml-daily.ru/daily_json.js"

# divide 1 by valute = opposite course
exchange_valute = lambda val1, val2: \
                    round((1 / val2) / (1 / val1), 3) 


# ---SIDE EFF SECTION---
# get data from api - convert to json
try:
    response = requests.get(url).json()
except Exception as err:
    import datetime
    with open('log.txt', 'w') as file:
        file.write(f'{datetime.datetime} {err}')

# get values by keys
# destructuring list to vars
dollar, euro, yuan, jpy = [response['Valute'][key]
                           for key in char_codes]

# не понимаю зачем нужно делить йены на 100, 
# но без этого формула ломается
jpy['Previous'] = jpy['Previous'] / 100


# ---DB SECTION---
# create tables
db.generate_mapping(create_tables=True)

# insert values
try:
    with db_session:
        [Valutes(
            char_code=val['CharCode'],
            name=val['Name'],
            to_usd=exchange_valute(val['Previous'],dollar['Previous']),
            to_eur=exchange_valute(val['Previous'],euro['Previous']),
            to_cny=exchange_valute(val['Previous'],yuan['Previous']),
            to_jpy=exchange_valute(val['Previous'],jpy['Previous'])
        ) for val in [dollar, euro, yuan, jpy]]

# empty >except because 
# if we try to copy unique values - we get an error
except:
    pass
