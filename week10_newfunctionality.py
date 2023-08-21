# written by Angela Hansen 8/20/2023
# code pulls most current close price from yahoo finance 
# code calculates total portfolio value, total change in value since purchase, percent change in value since purchase
# 

import yfinance as yf
import yfinance.shared as shared
from datetime import date, timedelta
import pandas as pd
import sqlite3 as db
from week10_portfolioclasses import Investors
import matplotlib.pyplot as plt

today = date.today()

csv_path = r"C:\Users\super\OneDrive\Documents\Hansen stuff\DU\ICT4370 python_work\Lesson6_Data_Stocks.csv"

# connect to database
conn = db.connect('week10investments.db')

# get stock symbols from db as list
conn.row_factory = lambda cursor, row: row[0]
c = conn.cursor()
c.execute('SELECT symbol FROM stocks')
symbol_list = c.fetchall() 

# get most recent business day date
diff = 1
if today.weekday() == 0:
    diff = 3
elif today.weekday() == 6:
    diff = 2
else :
    diff = 1

stock_date = today - timedelta(days=diff)


# get current close prices for the stocks
try:
    data = yf.download(symbol_list, stock_date) 
    failed_downloads = list(shared._ERRORS.keys())

    # make sure all stocks downloaded correctly
    for symbol in failed_downloads:
        if symbol:
            print(f'{symbol} failed to download. Please recheck the stock symbol and try again.')
except NameError:
    print("The symbol name could not be read.")

# correct stocks in the list that are incorrect
for i in range(len(symbol_list)):
    if symbol_list[i] == 'FB':
        symbol_list[i] = 'META'
    if symbol_list[i] == 'RDS-A':
        symbol_list[i] = 'SHEL'

# re-download data with fixed symbol list
data = yf.download(symbol_list, stock_date)

# reformat dataframe
current_prices_df = data.stack()

# change the df index from 'symbol' so I can align and merge the dataframes, update column names
df2 = (current_prices_df.reset_index(level=1)) 
df2.rename(columns = {'level_1':'SYMBOL'}, inplace=True)
df2.rename(columns= {'Close':'CURRENT_PRICE'}, inplace=True)

# open csv file, update incorrect symbols
csv_df = pd.read_csv(csv_path)
csv_df.loc[2,['SYMBOL']] = 'SHEL'
csv_df.loc[4,['SYMBOL']] = 'META'

# merge the dataframes, remove unneeded columns
df_merged = pd.merge(df2, csv_df, on=['SYMBOL'])

# create class instances from dataframe
inv_3 = Investors("Oliver Hansen", "13 Bokoblin Dr.", "236-2846")
for stock in df_merged:
    purchase_id = 0
    inv_3.add_stock(['SYMBOL'], ['NO_SHARES'], ['PURCHASE_PRICE'], ['CURRENT_PRICE'], ['PURCHASE_DATE'], purchase_id)
    purchase_id = purchase_id + 1

# remove unneeded data 
df_merged.drop(columns=['Adj Close', 'PURCHASE_DATE', 'CURRENT_VALUE', 'Open', 'High', 'Low', 'Volume'], inplace=True)


# calculate total portfolio value, change in value, percent change in value since purchase for each stock
df_merged['TOTAL VALUE'] = round((df_merged['CURRENT_PRICE'] * df_merged['NO_SHARES']), 2)
df_merged['TOTAL CHANGE IN VALUE'] = round((df_merged['TOTAL VALUE']) - (df_merged['NO_SHARES'] * df_merged['PURCHASE_PRICE']), 2)
df_merged['PERCENT CHANGE IN VALUE'] = round(((df_merged['CURRENT_PRICE'] - df_merged['PURCHASE_PRICE']) / df_merged['PURCHASE_PRICE']) * 100, 2)

# create variables for printing, calculate total portfolio value and change in value
total_value = df_merged['TOTAL VALUE'].sum()
total_purchase = (df_merged['NO_SHARES'] * df_merged['PURCHASE_PRICE']).sum()
total_change = total_value - total_purchase

def plot_stock(symbol):
    df_merged.plot(y='TOTAL VALUE')
    plt.legend(symbol_list)
    plt.title(f'Investment Value: {symbol}')
    plt.ylabel("Value")
    plt.savefig(f'{symbol}_figure')
    plt.show()

def print_current_investments(investor):
    """prints dataframe with investment information updated as of the previous business day"""
    print(Investors.__str__(investor))
    print(f"\n Here is information about your investments as of {stock_date.strftime('%b %d, %Y')}.\n")
    print(df_merged)
    print(f"\nToday, your stock portfolio is worth", '${:,.2f}'.format(total_value, '.2f'))
    if total_change > 0:
        print(f"You have earned a total of", '${:,.2f}'.format(total_change, '.2f'))
    elif total_change < 0:
        print("Since you started investing, you have lost a total of", '${:,.2f}'.format(abs(total_change), '.2f'))
    else:
        print("You have not gained or lost any money.")

if __name__ == '__main__':
    print_current_investments(inv_3)