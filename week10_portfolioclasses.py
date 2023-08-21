#Angela Hansen, updated 8/20/23
"""stocks and bonds classes: provide info about stocks and bonds purchased"""

from tabulate import tabulate
import csv
from datetime import datetime, date

current_date = date.today()

#create class for stocks
class Stocks:
    def __init__(self, symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id):
        self.symbol = symbol
        self.number_shares = number_shares
        self.purchase_price = purchase_price
        self.current_cost = current_cost
        self.purchase_date = purchase_date
        self.purchase_id = purchase_id
        self.earnings_loss = []
        self.percent_earning = []

#create methods for Stocks class
    
    def loss_gain(self):
        """calculates the amount earned and lost for each purchase"""
        earnings_loss = (self.current_cost - self.purchase_price) * self.number_shares
        self.earnings_loss.append(earnings_loss)
        return earnings_loss

    def calc_percent_earning(self):
        """function to calculate percentage yield/loss per stock"""
        percent_earning = (((self.current_cost - self.purchase_price) / self.purchase_price))/((current_date-self.purchase_date).days * 365 * 100)
        self.percent_earning.append(percent_earning)
        return percent_earning

    def get_stock_data(self):
        return [self.symbol.upper(), self.number_shares, '${:,.2f}'.format(Stocks.loss_gain(self), '.2f'), Stocks.calc_percent_earning(self)]
    

#create class for json stocks, any stocksjson members must have additional purchase price etc info
class StocksJSON:
    def __init__(self, symbol, date, open_price, high_price, low_price, close_price, volume, purchase_id):
        self.symbol = symbol
        self.date = date
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.volume = volume
        self.purchase_id = purchase_id

    def __str__(self):
        return str(self.close_price)
    
#create class for bonds
class Bonds(Stocks):
    def __init__(self, symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id, coupon, yield_bond):
        super().__init__(symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id)
        self.coupon = coupon
        self.yield_bond = yield_bond
        self.earnings_bond = []

    def bond_gain(self):
        """calculates the total amount earned for each bond purchase"""
        earnings_bond = self.current_cost - self.purchase_price
        self.earnings_bond.append(earnings_bond)
        return earnings_bond

    def get_bond_data(self):
        return [self.symbol.upper(), self.number_shares, Bonds.bond_gain(self), self.coupon, self.yield_bond]


#create class for investors with address and phone number
class Investors:
    def __init__(self, name, address, phone):
        self.name = name
        self.address = address
        self.phone = phone
        self.stocks = []
        self.bonds = []
        self.json_stocks = []

    def add_stock(self, symbol, purchase_price, current_price, quantity, purchase_date, purchase_id):
        stock = Stocks(symbol, purchase_price, current_price, quantity, purchase_date, purchase_id)
        self.stocks.append(stock)

    def add_bond(self, symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id, coupon, yield_bond):
        bond = Bonds(symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id, coupon, yield_bond)
        self.bonds.append(bond)

    def add_json_stock(self, symbol, date, open_price, high_price, low_price, close_price, volume, purchase_id):
        json_stock = StocksJSON(symbol, date, open_price, high_price, low_price, close_price, volume, purchase_id)
        self.json_stocks.append(json_stock)

    def get_stock_table(self):
        headers = ["Symbol", "Quantity", "Earnings/Loss", "Yearly Earning/Loss"]
        data = [stock.get_stock_data() for stock in self.stocks]
        return tabulate(data, headers=headers, tablefmt="grid")

    def get_bond_table(self): 
        headers = ["Symbol", "Quantity", "Earnings/Loss", "Coupon", "Yield"]
        data = [bond.get_bond_data() for bond in self.bonds]
        return tabulate(data, headers=headers, tablefmt="grid")
    
    def __str__(self):
        return f"Investor Name:  {self.name}\nAddress: {self.address}\nPhone: {self.phone}"
    

#print stock info
#add conditional statement to keep this code from printing in other files
#instantiate Bob Smith and his stocks/bonds
if __name__ == '__main__':
    bs_01 = Investors("Bob Smith", "123 Python Way", "867-5309")
    # open csv file, write info to table
    with open('Lesson6_Data_Stocks.csv', 'r') as sf:
        csvreader = csv.reader(sf)
        fields = next(csvreader)
        purchase_id = 1
        for symbol, number_shares, purchase_price, current_price, purchase_date in csvreader:
            number_shares = int(number_shares)
            purchase_price = float(purchase_price)
            current_price = float(current_price)
            purchase_date = datetime.strptime(purchase_date, '%m/%d/%Y').date()
            purchase_id = purchase_id + 1
            #populate the stock data into the stocks table
            bs_01.add_stock(symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id)
    
    #open bonds file, write bonds to  table
    with open('Lesson6_Data_Bonds.csv', 'r') as bf:
        csvreader = csv.reader(bf)
        fields = next(csvreader)
        purchase_id = 0
        for symbol, number_shares, purchase_price, current_price, purchase_date, coupon, yield_bond in csvreader:
            number_shares = int(number_shares)
            purchase_price = float(purchase_price)
            current_price = float(current_price)
            purchase_date = datetime.strptime(purchase_date, '%m/%d/%Y').date()
            coupon = float(coupon)
            yield_bond = float(yield_bond)
            purchase_id = purchase_id + 1
            #populate the bond data into the bonds table
            bs_01.add_bond(symbol, number_shares, purchase_price, current_price, purchase_date, purchase_id, coupon, yield_bond)
    
    print(Investors.__str__(bs_01))
    print("\nStock Information:")
    print(Investors.get_stock_table(bs_01))
    print("\nBond Information:")
    print(Investors.get_bond_table(bs_01))
