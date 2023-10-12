import json
from tkinter import *


import requests
from dateutil import parser
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

from tk_NBPupg import window_initialization, windows_init, result_frame_inti, clear_result_frame

DEFAULT_CURRENCY = "USD"
DATA_FORMAT = "%Y-%m-%d"
URL_BETWEEN = "http://api.nbp.pl/api/exchangerates/rates/a/{currency}/{date_start}/{date_end}/?format=json"


def validate_currency(currency:str) -> None:
    if not currency.isalpha() or len(currency) != 3:
        raise ValueError("Invalid currency format. Please provide a 3-letter currency code.")

def check_currency_code_exists() -> List[str]:
    with open('currency_codes.txt', 'r') as file:
        codes = file.read().splitlines()
        return codes


def validate_date(date_start:str, date_end:str) -> Tuple[str]:
    try:
        date_parsed_start = parser.parse(date_start)
        date_start = date_parsed_start.strftime(DATA_FORMAT)
        date_parsed_end = parser.parse(date_end)
        date_end = date_parsed_end.strftime(DATA_FORMAT)
    except ValueError:
        raise ValueError("Invalid date format. Please provide the date in YYYY-MM-DD format.")


    if date_parsed_start.year < 2002 and date_parsed_end.year < 2002:
        raise ValueError("Invalid year. Please provide a year after 2001.")


    if date_parsed_start.date() > datetime.now().date() or date_parsed_end.date() > datetime.now().date():
        raise ValueError("Invalid date. Please provide a date in the past.")
        

    return date_start, date_end

def get_exchange_rate(currency:str, date_start:str, date_end:str) -> Dict:
    url = URL_BETWEEN.format(currency=currency, date_start=date_start, date_end=date_end)
    resp = requests.get(url)

    if resp.status_code == 404:
        raise ValueError("No data. You probably chose a day off.")

    if not resp.ok: #How to test?
        raise ValueError("Unexpected server response")

    return resp.json()

def extract_currency_rates(resp_js:Dict) -> List:
    try:    
        currency_rates = [item["mid"] for item in resp_js["rates"]]
    
    except json.decoder.JSONDecodeError:
        raise ValueError("No data")
    
    except KeyError:
        raise KeyError("Empty key")
    
    except TypeError:
        raise TypeError("Invalid data")

    return currency_rates


def label_show_init(result_frame, currency_rates, currency, dates):
    clear_result_frame(result_frame)
    
    for i, c in enumerate(currency_rates):
        result = f"1 {currency.upper()} = {c} PLN on the day {dates[i]}"
        label = Label(result_frame, text=result, width=52, anchor=W)
        label.pack()


def button_init(root, result_frame, entries):

    def on_button_click():
        currency = entries[0].get() if entries[0].get() else DEFAULT_CURRENCY
        date_start = entries[1].get() if entries[1].get() else (datetime.now()-timedelta(days=6)).strftime(DATA_FORMAT)
        date_end = entries[2].get() if entries[2].get() else datetime.now().strftime(DATA_FORMAT)

        try:
            validate_currency(currency)
            date_start, date_end = validate_date(date_start, date_end)
            resp_js = get_exchange_rate(currency, date_start, date_end)
            currency_rates = extract_currency_rates(resp_js)
            dates = [item["effectiveDate"] for item in resp_js["rates"]]

            label_show_init(result_frame, currency_rates, currency, dates)

        except ValueError as e:
            print(e)

    button = Button(root, text="Show", command=on_button_click)
    button.grid(row=2, column=0, columnspan=2, padx=(210, 0), pady=10)
    button.config(background='green', foreground='white')
    return button


codes = check_currency_code_exists()

def main():
    root = window_initialization()
    frame, entries = windows_init(root)
    result_frame = result_frame_inti(root)
    clear_result_frame(result_frame)
    button = button_init(root, result_frame, entries)
    root.mainloop()

if __name__ == '__main__':
    main()