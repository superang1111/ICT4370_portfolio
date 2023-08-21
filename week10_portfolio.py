"""
Written by Angela Hansen 8/20/23
This program imports stock data from a JSON file, writes it to the StocksJSON class,
writes it to a database, and creates a line graph of stock values. 
Stock values are calculated based on number of shares pulled from the database that I created earlier
New functionality is pulled in from 'current_stock_prices.py' through the function 'print_current_investments'
'current_stock_prices.py': code pulls most current close price from yahoo finance 
code calculates total portfolio value, total change in value since purchase, percent change in value since purchase

"""

from week10_portfolioclasses import Investors
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
from datetime import datetime
import sqlite3
from week10_newfunctionality import*
import pandas as pd

json_path = r'C:\Users\super\OneDrive\Documents\Hansen stuff\DU\ICT4370 python_work\week8 work portfolio\AllStocks.json'
stocks_path = r"C:\Users\super\OneDrive\Documents\Hansen stuff\DU\ICT4370 python_work\Lesson6_Data_Stocks.csv"
bonds_path = r"C:\Users\super\OneDrive\Documents\Hansen stuff\DU\ICT4370 python_work\Lesson6_Data_Bonds.csv"

# create database
conn = sqlite3.connect('week10investments.db')

#create a cursor
c = conn.cursor()

#create database tables
# the investor table is the parent table
c.execute("""CREATE TABLE IF NOT EXISTS investors (
          investor_id text PRIMARY KEY,
          name text NOT NULL, 
          address text NOT NULL,
          phone text)
    """)

conn.commit() #commit the connection, executes/pushes info into the database

c.execute("""CREATE TABLE IF NOT EXISTS stocks (
          symbol text NOT NULL,
          number_shares integer,
          purchase_price real,
          current_price real,
          purchase_date date,
          purchase_id integer,
          investor_id text NOT NULL,
          FOREIGN KEY (investor_id) REFERENCES investors (invester_id))
    """)

conn.commit() 

c.execute("""CREATE TABLE IF NOT EXISTS bonds (
          symbol text NOT NULL, 
          number_shares integer,
          purchase_price real,
          current_price real,
          purchase_date date,
          purchase_id integer NOT NULL,
          coupon real,
          yield real,
          investor_id text NOT NULL,
          FOREIGN KEY (investor_id) REFERENCES investors (invester_id))
    """)

conn.commit() 

c.execute("""CREATE TABLE IF NOT EXISTS json_stocks (
          symbol text NOT NULL, 
          date date,
          opening_price real,
          high_price real,
          low_price real,
          close_price real, 
          volume integer,
          investor_id text NOT NULL,
          FOREIGN KEY (investor_id) REFERENCES investors (invester_id))
    """)

#instantiate an investor
inv_2 = Investors("Angela Hansen", "42 ThisIsThe Way", "477-1042")

def insert_into_investors_database(investor):
    c.execute("INSERT or IGNORE INTO investors (investor_id, name, address, phone) VALUES (?,?,?,?)",
            (str(investor), investor.name, investor.address, investor.phone))
    conn.commit() 

# open json file and load data
with open(json_path) as jf:
    json_data = json.load(jf)

# open investor csv file and load into list of dictionaries
investor_data = []
with open(stocks_path, 'r') as sf:
    csvreader = csv.DictReader(sf)
    for row in csvreader:
        investor_data.append(row)


# load data into database from json file
# json data loads as a list of dictionaries
def insert_stock_to_database(stock_data):
    """inserts raw stock data into database"""
    for record in stock_data:
        c.execute("INSERT INTO json_stocks VALUES (:Symbol, :Date, :Open, :High, :Low, :Close, :Volume, 'inv_2')", record)
    conn.commit()

# open stock purchase info file
def insert_stock_inv_to_database(stock_path):
    """instantiate investment data to Stocks class, write data to database"""
    with open(stock_path, 'r') as sf:
        csvreader = csv.reader(sf)
        fields = next(csvreader)

        #instantiate stock purchase data into Stocks class
        purchase_id = 1
        for symbol, number_shares, purchase_price, current_price, purchase_date in csvreader:
            number_shares = int(number_shares)
            purchase_price = float(purchase_price)
            current_price = float(current_price)
            purchase_date = datetime.strptime(purchase_date, '%m/%d/%Y').date()
            purchase_id = purchase_id + 1
            inv_2.add_stock(symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id)
            
            #insert stock purchase data into database
            c.execute("INSERT INTO stocks (symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id, investor_id) VALUES (?,?,?,?,?,?,?)", 
                    (symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id, 'inv_2'))


def stock_data_to_plot(investor_data, stock_data):
    """stores stock data in dictionary for plotting"""
    plot_data = {} # keys are symbol names, values are lists of dates and values
    for json_record in stock_data: # json data is a list of dictionaries from the json file
        symbol = json_record['Symbol']
        date = datetime.strptime(json_record['Date'], '%d-%b-%y') 
        price = float(json_record['Close'])
        if symbol not in plot_data:
            plot_data[symbol] = {'dates': [], 'price': []}
        
        plot_data[symbol]['dates'].append(date)
        plot_data[symbol]['price'].append(price)

    for purchase_info in investor_data: 
        symbol = purchase_info['SYMBOL']
        number_shares = float(purchase_info['NO_SHARES'])
        purchase_date = datetime.strptime(purchase_info['PURCHASE_DATE'], '%m/%d/%Y')

        plot_data[symbol]['price'] = [format((price * number_shares), '.2f') if date >= purchase_date else price
                                            for date, price in zip(plot_data[symbol]['dates'], plot_data[symbol]['price'])]
    # returns a dictionary where keys aresymbols and values are lists of dates and calculated stock values
    return plot_data


def insert_bond_inv_to_database(bonds_file_path):
    """instantiates bonds from investor data and inserts into database"""
    with open(bonds_file_path, 'r') as bf:
        csvreader = csv.reader(bf)
        fields = next(csvreader)

        #instantiate bond purchase data into Bonds class
        purchase_id = 0
        for symbol, number_shares, purchase_price, current_price, purchase_date, coupon, yield_bond in csvreader:
            number_shares = int(number_shares)
            purchase_price = float(purchase_price)
            current_price = float(current_price)
            purchase_date = datetime.strptime(purchase_date, '%m/%d/%Y').date()
            coupon = float(coupon)
            yield_bond = float(yield_bond)
            purchase_id = purchase_id + 1

            # insert bond purchase data into database
            inv_2.add_bond(symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id, coupon, yield_bond)
            c.execute("INSERT INTO bonds (symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id, coupon, yield, investor_id) VALUES (?,?,?,?,?,?,?,?,?)", 
                    (symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id, coupon, yield_bond, 'inv_2'))


def print_investment_info(investor):
    """prints stock and bond data in table format"""
    print(Investors.__str__(investor))
    print("\nStock Information:")
    print(Investors.get_stock_table(investor))
    print("\nBond Information:")
    print(Investors.get_bond_table(investor))

def add_to_db(investor, stock_data, stock_investor_data, bond_investor_data):
    """adds stock data, investment stock/bond data, investor data to database"""
    insert_into_investors_database(investor)
    insert_stock_to_database(stock_data)
    insert_stock_inv_to_database(stock_investor_data)
    insert_bond_inv_to_database(bond_investor_data)

    conn.commit()
    conn.close()


def plot_investment_data(dataframe):
    """this doesn't work"""
    dataframe['Close'].plot()
    plt.xlabel('Date')
    plt.ylabel('Stock Value')
    plt.title('Stock Value Over Time')
    plt.show()
    plt.legend()
    plt.savefig('stock_value_chart.png')
    plt.show()

# read data from json stock file
json_df = pd.read_json(json_path)

# make date the index row, drop unneeded columns
json_df = (json_df.set_index('Date')) 
json_df.drop(columns=['Open', 'High', 'Low', 'Volume'], inplace=True)

    
if __name__ == '__main__':
    print_investment_info(inv_2)
    print('\n\n')
    print_current_investments(inv_2)
    add_to_db(inv_2, json_data, stocks_path, bonds_path)
    plot_stock('GOOG')










