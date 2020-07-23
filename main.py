import requests
import matplotlib.pyplot as plt
from db import db, db_session, Valutes


# ---PURE SECTION---
char_codes = ['USD', 'EUR', 'CNY', 'JPY']

# api link
url = "https://www.cbr-xml-daily.ru/daily_json.js"

# days count == num of page to parse
days = 30

# divide 1 by valute -> opposite course
# (float, list) -> list(float)
exchange_to = lambda valute, valutes: \
                    [round((1 / v) / (1 / valute), 3) for v in valutes]

# (map) -> list
exchange_list = lambda valutes: \
                    [exchange_to(v, valutes) for v in valutes]

# divide valute course by nominal -> cost of unit of currency
# (list, int) -> float
nominal_to_one = lambda valute, nominal: \
                    round(valute / nominal, 3)

# ---SIDE EFF SECTION---
# get currency for each day of the month
# (map, string, int) -> map
def get_currency(valutes, url, days):
    try:
        # if map empty, create it
        if not valutes:
            # map structure ->
            # valutes[char_code] : [list of maps {} {} {} ...]
            # valutes['EXCHANGE'] : [[list of 4 lists with daily valute after exchange]] [[] [] [] []] ...] 
            valutes = {key: [] for key in char_codes}
            valutes['EXCHANGE'] = []
        # length of every list must eq then days count
        if len(valutes[char_codes[-1]]) != days:
            response = requests.get(url).json()
            # format all values to unit of currency
            values = [nominal_to_one(
                            response['Valute'][c]['Value'], 
                            response['Valute'][c]['Nominal']) 
                            for c in char_codes]               
            [valutes['EXCHANGE'].append({'values': exchange_list(values), 
                                    'date': response['Timestamp'][5:10]})]
            # append every daily valute to map                       
            [valutes[c].append(
                {'value': v,
                'date': response['Timestamp'][5:10]}) 
                for c, v in zip(char_codes, values)]
            # recursion
            get_currency(valutes, f"https:{response['PreviousURL']}", days)
        return valutes
    except Exception as err:
        import datetime
        with open('log.txt', 'w') as file:
            file.write(f'{datetime.datetime.now()} - {err}')

valutes = get_currency({}, url, days)

# ---DB SECTION---
# create tables
db.generate_mapping(create_tables=True)

# insert values
with db_session:
    [[Valutes(
        char_code=c,
        date=valute['date'],
        to_usd=value[0],
        to_eur=value[1],
        to_cny=value[2],
        to_jpy=value[3])
        for c, value in zip(char_codes, valute['values'])] 
            for valute in valutes['EXCHANGE']]

# ---DATA VISUALIZATION SECTION---
# get dates
dates = [valute['date'][3:] for valute in valutes['EXCHANGE']]

# before 20 19 18 17 -> after 7 18 19 20
dates.reverse()

# destructuring valute lists for variables -> 
# vars x4 =[[float list] [float list] [float list] [float list]]
usd, eur, cny, jpy = [[valute['value'] 
                        for valute in valutes[key]] 
                            for key in valutes if key != 'EXCHANGE']
                            
# sugar for call matplotlib func
# ([float list], str, char) -> None
def show(valute, label, color):
    plt.plot(valute, label=label, c=color)
    plt.legend()
    plt.show()

[show(valute, label, color) 
    for valute, label, color in zip(
                                [usd, eur, cny, jpy], 
                                char_codes, 
                                ['b', 'r', 'g', 'y'])]                    
