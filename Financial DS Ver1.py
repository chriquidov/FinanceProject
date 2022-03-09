import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from datetime import date

st.write("""
# Final Project Financial DS Dov&Moshe
""")

#Import the data until 25/2/2022 from Github
Prices_Weekly = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Prices_Weekly.csv', index_col='Date')
Prices_Daily = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Prices_Daily.csv', index_col='Date')
Volume_Weekly = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Volume_Weekly.csv', index_col='Date')
Volume_Daily = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Volume_Daily.csv', index_col='Date')

#Download data from 25/2/2022 until today from Yfinance
tickers = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
start = datetime.datetime(2022, 2, 27)
today = date.today()
end = datetime.datetime(today.year, today.month, today.day)
Prices_Weekly2 = yf.download(tickers, start=start, end=end, interval='1wk')['Adj Close']
Prices_Daily2 = yf.download(tickers, start=start, end=end, interval='1d')['Adj Close']
Volume_Weekly2 = yf.download(tickers, start=start, end=end, interval='1wk')['Volume']
Volume_Daily2 = yf.download(tickers, start=start, end=end, interval='1wk')['Volume']


#Convert all dates to the same format
Prices_Weekly['Date'] = pd.to_datetime(Prices_Weekly.index)
Prices_Weekly.set_index('Date',inplace=True)
Prices_Daily['Date'] = pd.to_datetime(Prices_Daily.index)
Prices_Daily.set_index('Date',inplace=True)
Volume_Weekly['Date'] = pd.to_datetime(Volume_Weekly.index)
Volume_Weekly.set_index('Date',inplace=True)
Volume_Daily['Date'] = pd.to_datetime(Volume_Daily.index)
Volume_Daily.set_index('Date',inplace=True)
Prices_Weekly2['Date'] = pd.to_datetime(Prices_Weekly2.index)
Prices_Weekly2.set_index('Date',inplace=True)
Prices_Daily2['Date'] = pd.to_datetime(Prices_Daily2.index)
Prices_Daily2.set_index('Date',inplace=True)
Volume_Weekly2['Date'] = pd.to_datetime(Volume_Weekly2.index)
Volume_Weekly2.set_index('Date',inplace=True)
Volume_Daily2['Date'] = pd.to_datetime(Volume_Daily2.index)
Volume_Daily2.set_index('Date',inplace=True)

#Merge the dataframes so there are 4 files in total.
Frames_Prices_Weekly = [Prices_Weekly, Prices_Weekly2]
Frames_Prices_Daily = [Prices_Daily, Prices_Daily2]
Frames_Volume_Weekly = [Volume_Weekly, Volume_Weekly2]
Frames_Volume_Daily = [Volume_Daily, Volume_Daily2]
Prices_Weekly = pd.concat(Frames_Prices_Weekly)
Prices_Daily = pd.concat(Frames_Prices_Daily)
Volume_Weekly = pd.concat(Frames_Volume_Weekly)
Volume_Daily = pd.concat(Frames_Volume_Daily)

if st.checkbox('Show raw data'):
    st.subheader('Raw data for Prices Weekly')
    st.dataframe(Prices_Weekly)
    st.subheader('Raw data for Prices Daily')
    st.dataframe(Prices_Daily)
    st.subheader('Raw data for Volume Weekly')
    st.dataframe(Volume_Weekly)
    st.subheader('Raw data for Volume Daily')
    st.dataframe(Volume_Daily)



#Select tickers for the simulation
tickers_simulation = st.multiselect(
     'What tickers would you like to see?',
     ('XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ'), default=['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ'])

# NEED TO WORK ON THIS ONE
if tickers_simulation == []:
    print('Error! Please enter at least one ticker')


#Select dates for the simulation
start_date = st.date_input(
     "What is the simulation start day?",
     dt.date(2010, 1, 1), min_value=dt.date(2010, 1, 1), max_value=None)

end_date = st.date_input(
     "What is the simulation end day?",
     date.today(), min_value=start_date, max_value=None)

start_date_f = dt.datetime(start_date.year, start_date.month, start_date.day)
end_date_f = dt.datetime(end_date.year, end_date.month, end_date.day)


#Remove the unwanted data from our files
week_prices = Prices_Weekly
tickers = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
for ticker in tickers:
    if ticker not in tickers_simulation:
        week_prices = week_prices.drop(columns=[ticker])
week_prices = week_prices[(week_prices.index >= start_date_f) & (week_prices.index <= end_date_f)]

#check error when there is no data

st.dataframe(week_prices)

week_prices.dropna(inplace=True)
week_changes=week_prices.pct_change()*100
week_changes['best_sector']=week_changes.idxmax(axis=1)
week_changes['worst_sector']=week_changes[week_changes.columns.difference(['best_sector'])].idxmin(axis=1)





warnings.filterwarnings("ignore")


today = start_date
simend = date.today()
tickers = tickers_simulation
transactionid = 0
money = 1000000
portfolio = {}
activelog = []
transactionlog = []


def getprice(date, ticker):
    global week_prices
    try:
        price = week_prices.loc[str(date)][ticker]
        return price
    except Exception as e:
        return None


def transaction(id, ticker, amount, price, type,profit):
    global transactionid
    if type == "buy":
        exp_date = today + dt.timedelta(days=7)
        transactionid += 1
    else:
        exp_date = today
    if type == "sell":
        data = {"id": id, "ticker": ticker, "amount": amount, "price": price, "date": today, "type": type,
                "exp_date": exp_date, "profit": profit}
    elif type == "buy":
        data = {"id": transactionid, "ticker": ticker, "amount": amount, "price": price, "date": today, "type": type,
                "exp_date": exp_date, "profit": profit}
        activelog.append(data)
    transactionlog.append(data)


def buy(interestlst, allocated_money):
    global money, portfolio
    for item in interestlst:
        price = getprice(today, item)
        if not pd.isnull(price):
            quantity = math.floor(allocated_money/price)
            if money >= quantity*price:
                money -= quantity*price
                portfolio[item] += quantity
                transaction(0, item, quantity, price, "buy", 0)


def sell():
    global money, portfolio, week_prices, today
    itemstoremove = []
    for i in range(len(activelog)):
        log = activelog[i]
        if log["exp_date"] <= today and log["type"] == "buy":
            tickprice = getprice(today, log["ticker"])
            if not pd.isnull(tickprice):
                money += log["amount"]*tickprice
                portfolio[log["ticker"]] -= log["amount"]
                profit = log["amount"]*tickprice - log["amount"]*log["price"]
                transaction(log["id"], log["ticker"], log["amount"], tickprice, "sell",profit)
                itemstoremove.append(i)
            else:
                log["exp_date"] += dt.timedelta(days=1)
    itemstoremove.reverse()
    for elem in itemstoremove:
        activelog.remove(activelog[elem])


def simulation():
    global today, week_changes, money
    start_date = today - dt.timedelta(days=7)
    interestlst = []
    interestlst.append(week_changes.loc[str(today)].worst_sector)
    sell()
    if len(interestlst) > 0:
        #moneyToAllocate = 500000/len(interestlst)
        moneyToAllocate = currentvalue()/(len(interestlst))
        buy(interestlst, moneyToAllocate)


# def getindices():
#     global tickers
#     f = open(r"C:\Users\chriq\Mon Drive\2022\Financial DS\Final_project\sectors.txt", "r")
#     for line in f:
#         tickers.append(line.strip())
#     f.close()


def tradingday():
    global week_prices, today
    return np.datetime64(today) in list(week_prices.index.values)


def currentvalue():
    global money, portfolio, today, week_prices
    value = money
    for ticker in tickers:
        tickprice = getprice(today, ticker)
        if not pd.isnull(tickprice):
            value += portfolio[ticker]*tickprice
    return int(value*100)/100


def main():
    global today
    #getindices()
    for ticker in tickers:
        portfolio[ticker] = 0
    while today <= simend:
        while not tradingday():
            today += dt.timedelta(days=1)
        simulation()
        currentpvalue = currentvalue()
        st.write(currentpvalue, today)
        today += dt.timedelta(days=7)

    df = pd.DataFrame(transactionlog)
    df.to_csv('transactions_worstsect.csv',index=False)
    st.dataframe(df)

main()