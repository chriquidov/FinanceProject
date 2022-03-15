import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
import numpy as np
import math
import warnings
from datetime import date, timedelta
import plotly.express as px
from streamlit_option_menu import option_menu
from urllib.error import URLError

st.write("""
# Final Project Financial DS Dov&Moshe
""")



#Import the data until 25/2/2022 from Github
Prices_Weekly = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Prices_Weekly.csv', index_col='Date')
Volume_Weekly = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Volume_Weekly.csv', index_col='Date')

#Download data from 25/2/2022 until today from Yfinance
tickers = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
start = dt.datetime(2022, 2, 27)
today = date.today()
end = dt.datetime(today.year, today.month, today.day)
Prices_Weekly2 = yf.download(tickers, start=start, end=end, interval='1wk')['Adj Close']
Volume_Weekly2 = yf.download(tickers, start=start, end=end, interval='1wk')['Volume']


#Convert all dates to the same format
Prices_Weekly['Date'] = pd.to_datetime(Prices_Weekly.index)
Prices_Weekly.set_index('Date',inplace=True)

Volume_Weekly['Date'] = pd.to_datetime(Volume_Weekly.index)
Volume_Weekly.set_index('Date',inplace=True)
Prices_Weekly2['Date'] = pd.to_datetime(Prices_Weekly2.index)
Prices_Weekly2.set_index('Date',inplace=True)
Volume_Weekly2['Date'] = pd.to_datetime(Volume_Weekly2.index)
Volume_Weekly2.set_index('Date',inplace=True)

#Merge the dataframes so there are 4 files in total.
Frames_Prices_Weekly = [Prices_Weekly, Prices_Weekly2]
Frames_Volume_Weekly = [Volume_Weekly, Volume_Weekly2]
Prices_Weekly = pd.concat(Frames_Prices_Weekly)
Volume_Weekly = pd.concat(Frames_Volume_Weekly)

if st.checkbox('Show raw data'):
    st.subheader('Raw data for Prices Weekly')
    st.dataframe(Prices_Weekly)
    st.subheader('Raw data for Volume Weekly')
    st.dataframe(Volume_Weekly)



with st.sidebar:
    selected = option_menu("Strategies", ['Best Sector', 'Worst Sector','Interval Strategy Weekly', 'Volume Strategy', 'Market Strategy', 'Interval Strategy Daily'], 
        icons=['hand-thumbs-up', 'hand-thumbs-down', 'calendar-week', 'volume-up-fill', 'house-door', 'calendar-day'], menu_icon="currency-dollar", default_index=0)

st.sidebar.write("---------")

#Select tickers for the simulation
try:
    tickers_simulation = st.sidebar.multiselect(
        'What tickers would you like to see?',
        ('XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ'), default=['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ'])
    if not tickers_simulation:
        st.error("Please select at least one ticker.")
    else:

        # NEED TO WORK ON THIS ONE
        if tickers_simulation == []:
            print('Error! Please enter at least one ticker')


        #Select dates for the simulation
        start_date = st.sidebar.date_input(
            "What is the simulation start day?",
            dt.date(2022, 1, 1), min_value=dt.date(2010, 1, 1), max_value=None)

        end_date = st.sidebar.date_input(
            "What is the simulation end day?",
            date.today() - timedelta(days=1), min_value=start_date, max_value=None)

        start_date_f = dt.datetime(start_date.year, start_date.month, start_date.day)
        end_date_f = dt.datetime(end_date.year, end_date.month, end_date.day)

        #Remove the unwanted data from our files
        tickers = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
        for ticker in tickers:
            if ticker not in tickers_simulation:
                Prices_Weekly = Prices_Weekly.drop(columns=[ticker])
                Volume_Weekly = Volume_Weekly.drop(columns=[ticker])
        Prices_Weekly = Prices_Weekly[(Prices_Weekly.index >= start_date_f) & (Prices_Weekly.index <= end_date_f)]
        Volume_Weekly = Volume_Weekly[(Volume_Weekly.index >= start_date_f) & (Volume_Weekly.index <= end_date_f)]

        week_prices = Prices_Weekly

        #Functions around the simulation
        warnings.filterwarnings("ignore")

        today = start_date
        simend = end_date
        tickers = tickers_simulation
        transactionid = 0
        money = 1000000
        initial_money = money
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



        def currentvalue():
            global money, portfolio, today, week_prices
            value = money
            for ticker in tickers:
                tickprice = getprice(today, ticker)
                if not pd.isnull(tickprice):
                    value += portfolio[ticker]*tickprice
            return int(value*100)/100


        if selected == "Best Sector":
            week_changes=week_prices.pct_change()*100
            week_changes['best_sector']=week_changes.idxmax(axis=1)
            week_changes['worst_sector']=week_changes[week_changes.columns.difference(['best_sector'])].idxmin(axis=1)

            st.write("This is the dataframe this strategy works on. See the last two columns, best and worst sectors")
            st.dataframe(week_changes)

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

            def tradingday():
                global week_prices, today
                return np.datetime64(today) in list(week_prices.index.values)

            def simulation():
                global today, week_changes, money
                start_date = today - dt.timedelta(days=7)
                interestlst = []
                interestlst.append(week_changes.loc[str(today)].best_sector)
                sell()
                if len(interestlst) > 0:
                    moneyToAllocate = currentvalue()/(len(interestlst))
                    buy(interestlst, moneyToAllocate)

            def main():
                global today
                best_sectors_log = pd.DataFrame(columns=['Date','Current_Value'])
                for ticker in tickers:
                    portfolio[ticker] = 0
                while today <= simend:
                    while not tradingday():
                        today += dt.timedelta(days=1)
                    simulation()
                    currentpvalue = currentvalue()
                    best_sectors_log.loc[best_sectors_log.shape[0]] = [today, currentpvalue]
                    #st.write([today, currentpvalue])
                    today += dt.timedelta(days=7)

                st.write("\n\nThis is the graph of the portfolio value")

                fig = px.line(        
                        best_sectors_log, #Data Frame
                        x = "Date", #Columns from the data frame
                        y = "Current_Value",
                        title = "Best Sectors Strategy"
                    )
                fig.update_traces(line_color = "green")
                st.plotly_chart(fig)


                length = len(best_sectors_log) - 1
                st.write("With this method, the portfolio was worth {} on {} and today the portfolio is worth: ${}.".format(initial_money, start_date_f, best_sectors_log['Current_Value'][length]))

                performance_best_sectors = (((best_sectors_log['Current_Value'][length])/initial_money)-1)*100
                st.write("This is a fluctuation of {}% over the period.".format(round(performance_best_sectors, 3)))

                best_sectors_log = pd.DataFrame(transactionlog)
                best_sectors_log_str = pd.DataFrame.to_string(best_sectors_log)
                if st.download_button('Download Transaction File', best_sectors_log_str, 'Best_Sectors.txt'):
                    st.write('Thanks for downloading!')
                st.write("")

                best_sectors_log['Positive_return']=np.select([best_sectors_log['profit']>0 ,(best_sectors_log['profit']==0) & (best_sectors_log.type=='buy'),
                                 (best_sectors_log['profit']==0) & (best_sectors_log.type=='sell'),best_sectors_log['profit']<0],[1,None,-1,-1])

                occurences=[]
                tick_prof=[]
                avg_tick_profit=[]
                profitable=[]
                for ticker in tickers:
                    occurence=len(best_sectors_log.loc[best_sectors_log.ticker==ticker])/2
                    occurences.append(occurence)
                    tot_profit=round(best_sectors_log.loc[best_sectors_log.ticker==ticker].profit.sum(),1)
                    tick_prof.append(tot_profit)
                    avg_tick_profit.append(round(tot_profit/occurence,1))
                    if occurence > 0:
                        profitable.append(round(len(best_sectors_log.loc[(best_sectors_log.ticker==ticker)&(best_sectors_log.Positive_return>0)])/occurence,5)*100)
                    else:
                        profitable.append(0)
                best_sectors_stats=pd.DataFrame()
                best_sectors_stats['ticker']=tickers
                best_sectors_stats['occurences']=occurences
                best_sectors_stats['profit_from_ticker']=tick_prof
                best_sectors_stats['avg_profit']=avg_tick_profit
                best_sectors_stats['%_Positive_returns']=profitable

                st.write("Statistics on the Best Sectors strategy:")
                st.dataframe(best_sectors_stats, height=500)

                fig = px.bar(        
                        best_sectors_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "%_Positive_returns",
                        title = "Best Sectors Strategy Stats - Percentage of positive returns"
                    )
                st.plotly_chart(fig)

                fig = px.bar(        
                        best_sectors_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "profit_from_ticker",
                        title = "Best Sectors Strategy Stats - profit made from tickers"
                    )
                st.plotly_chart(fig)

            main()
        elif selected == "Worst Sector":
            week_changes=week_prices.pct_change()*100
            week_changes['best_sector']=week_changes.idxmax(axis=1)
            week_changes['worst_sector']=week_changes[week_changes.columns.difference(['best_sector'])].idxmin(axis=1)

            st.write("This is the dataframe this strategy works on. See the last two columns, best and worst sectors")
            st.dataframe(week_changes)

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

            def tradingday():
                global week_prices, today
                return np.datetime64(today) in list(week_prices.index.values)

            def simulation():
                global today, week_changes, money
                start_date = today - dt.timedelta(days=7)
                interestlst = []
                interestlst.append(week_changes.loc[str(today)].worst_sector)
                sell()
                if len(interestlst) > 0:
                    moneyToAllocate = currentvalue()/(len(interestlst))
                    buy(interestlst, moneyToAllocate)

            def main():
                global today
                worst_sectors_log = pd.DataFrame(columns=['Date','Current_Value'])
                for ticker in tickers:
                    portfolio[ticker] = 0
                while today <= simend:
                    while not tradingday():
                        today += dt.timedelta(days=1)
                    simulation()
                    currentpvalue = currentvalue()
                    worst_sectors_log.loc[worst_sectors_log.shape[0]] = [today, currentpvalue]
                    #st.write([today, currentpvalue])
                    today += dt.timedelta(days=7)

                st.write("\n\nThis is the graph of the portfolio value")

                fig = px.line(        
                        worst_sectors_log, #Data Frame
                        x = "Date", #Columns from the data frame
                        y = "Current_Value",
                        title = "Worst Sectors Strategy"
                    )
                fig.update_traces(line_color = "green")
                st.plotly_chart(fig)


                length = len(worst_sectors_log) - 1
                st.write("With this method, the portfolio was worth {} on {} and today the portfolio is worth: ${}.".format(initial_money, start_date_f, worst_sectors_log['Current_Value'][length]))

                performance_worst_sectors = (((worst_sectors_log['Current_Value'][length])/initial_money)-1)*100
                st.write("This is a fluctuation of {}% over the period.".format(round(performance_worst_sectors, 3)))

                worst_sectors_log = pd.DataFrame(transactionlog)
                worst_sectors_log_str = pd.DataFrame.to_string(worst_sectors_log)
                if st.download_button('Download Transaction File', worst_sectors_log_str, 'Worst_Sectors.txt'):
                    st.write('Thanks for downloading!')
                st.write("")

                worst_sectors_log['Positive_return']=np.select([worst_sectors_log['profit']>0 ,(worst_sectors_log['profit']==0) & (worst_sectors_log.type=='buy'),
                                 (worst_sectors_log['profit']==0) & (worst_sectors_log.type=='sell'),worst_sectors_log['profit']<0],[1,None,-1,-1])

                occurences=[]
                tick_prof=[]
                avg_tick_profit=[]
                profitable=[]
                for ticker in tickers:
                    occurence=len(worst_sectors_log.loc[worst_sectors_log.ticker==ticker])/2
                    occurences.append(occurence)
                    tot_profit=round(worst_sectors_log.loc[worst_sectors_log.ticker==ticker].profit.sum(),1)
                    tick_prof.append(tot_profit)
                    avg_tick_profit.append(round(tot_profit/occurence,1))
                    if occurence > 0:
                        profitable.append(round(len(worst_sectors_log.loc[(worst_sectors_log.ticker==ticker)&(worst_sectors_log.Positive_return>0)])/occurence,5)*100)
                    else:
                        profitable.append(0)
                worst_sectors_stats=pd.DataFrame()
                worst_sectors_stats['ticker']=tickers
                worst_sectors_stats['occurences']=occurences
                worst_sectors_stats['profit_from_ticker']=tick_prof
                worst_sectors_stats['avg_profit']=avg_tick_profit
                worst_sectors_stats['%_Positive_returns']=profitable

                st.write("Statistics on the Worst Sectors strategy:")
                st.dataframe(worst_sectors_stats, height=500)

                fig = px.bar(        
                        worst_sectors_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "%_Positive_returns",
                        title = "Worst Sectors Strategy Stats - Percentage of positive returns"
                    )
                st.plotly_chart(fig)

                fig = px.bar(        
                        worst_sectors_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "profit_from_ticker",
                        title = "Worst Sectors Strategy Stats - profit made from tickers"
                    )
                st.plotly_chart(fig)

            main()
        elif selected == "Interval Strategy Weekly":
            week_changes=week_prices.pct_change()*100
            nxt_w_chg=week_changes.shift(-1)

            st.write("This is the dataframe this strategy works on.")
            st.dataframe(nxt_w_chg)


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

            def tradingday():
                global week_prices, today
                return np.datetime64(today) in list(week_prices.index.values)

            def simulation():
                global today, week_changes, nxt_w_chg, money, tickers
                start_date = today - dt.timedelta(days=7)
                n=0.1
                d={}
                for ticker in tickers:
                    val=week_changes[ticker].loc[str(today)]
                    date_logic=week_changes.index<str(today)
                    exp_n=nxt_w_chg[ticker].loc[date_logic& (week_changes[ticker]>val-n)&(week_changes[ticker]<val+n)].mean()
                    std_n=nxt_w_chg[ticker].loc[date_logic& (week_changes[ticker]>val-n)&(week_changes[ticker]<val+n)].std()
                    if std_n != 0:
                        sharp=exp_n/std_n
                    else:
                        sharp=0
                    d[ticker]=exp_n
                interestlst = []
                interestlst.append(max(d, key=d.get))
                sell()
                if len(interestlst) > 0:
                    moneyToAllocate = currentvalue()/(len(interestlst))
                    buy(interestlst, moneyToAllocate)

            def main():
                global today
                weekly_interval_log = pd.DataFrame(columns=['Date','Current_Value'])
                for ticker in tickers:
                    portfolio[ticker] = 0
                while today <= simend:
                    while not tradingday():
                        today += dt.timedelta(days=1)
                    simulation()
                    currentpvalue = currentvalue()
                    weekly_interval_log.loc[weekly_interval_log.shape[0]] = [today, currentpvalue]
                    today += dt.timedelta(days=7)

                st.write("\n\nThis is the graph of the portfolio value")

                fig = px.line(        
                        weekly_interval_log, #Data Frame
                        x = "Date", #Columns from the data frame
                        y = "Current_Value",
                        title = "Weekly Interval Strategy"
                    )
                fig.update_traces(line_color = "green")
                st.plotly_chart(fig)


                length = len(weekly_interval_log) - 1
                st.write("With this method, the portfolio was worth {} on {} and today the portfolio is worth: ${}.".format(initial_money, start_date_f, weekly_interval_log['Current_Value'][length]))

                performance_weekly_interval = (((weekly_interval_log['Current_Value'][length])/initial_money)-1)*100
                st.write("This is a fluctuation of {}% over the period.".format(performance_weekly_interval))

                weekly_interval_log = pd.DataFrame(transactionlog)
                weekly_interval_log_str = pd.DataFrame.to_string(weekly_interval_log)
                if st.download_button('Download Transaction File', weekly_interval_log_str, 'Worst_Sectors.txt'):
                    st.write('Thanks for downloading!')

                weekly_interval_log['Positive_return']=np.select([weekly_interval_log['profit']>0 ,(weekly_interval_log['profit']==0) & (weekly_interval_log.type=='buy'),
                                 (weekly_interval_log['profit']==0) & (weekly_interval_log.type=='sell'),weekly_interval_log['profit']<0],[1,None,-1,-1])

                occurences=[]
                tick_prof=[]
                avg_tick_profit=[]
                profitable=[]
                for ticker in tickers:
                    occurence=len(weekly_interval_log.loc[weekly_interval_log.ticker==ticker])/2
                    occurences.append(occurence)
                    tot_profit=round(weekly_interval_log.loc[weekly_interval_log.ticker==ticker].profit.sum(),1)
                    tick_prof.append(tot_profit)
                    avg_tick_profit.append(round(tot_profit/occurence,1)) 
                    if occurence > 0:
                        profitable.append(round(len(best_sectors_log.loc[(best_sectors_log.ticker==ticker)&(best_sectors_log.Positive_return>0)])/occurence,5)*100)
                    else:
                        profitable.append(0)
                weekly_interval_stats=pd.DataFrame()
                weekly_interval_stats['ticker']=tickers
                weekly_interval_stats['occurences']=occurences
                weekly_interval_stats['profit_from_ticker']=tick_prof
                weekly_interval_stats['avg_profit']=avg_tick_profit
                weekly_interval_stats['%_Positive_returns']=profitable

                st.write("Statistics on the Best Sectors strategy:")
                st.dataframe(weekly_interval_stats, height=500)

                fig = px.bar(        
                        weekly_interval_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "%_Positive_returns",
                        title = "Weekly Intervals Strategy Stats - Percentage of positive returns"
                    )
                st.plotly_chart(fig)

                fig = px.bar(        
                        weekly_interval_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "profit_from_ticker",
                        title = "Weekly Intervals Strategy Stats - profit made from tickers"
                    )
                st.plotly_chart(fig)

            main()
        elif selected == "Volume Strategy":
            prices = Prices_Weekly
            volumechanges = Volume_Weekly.pct_change()*100

            st.write("This is the dataframe this strategy works on.")
            st.dataframe(volumechanges)

            def transaction(id, ticker, amount, price, type,profit):
                global transactionid
                if type == "buy":
                    exp_date = today + dt.timedelta(days=1)
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

            def tradingday():
                global day_prices, today
                return np.datetime64(today) in list(volumechanges.index.values)

            def simulation():
                global today, volumechanges, money
                start_date = today - dt.timedelta(days=1)
                series = volumechanges.loc[start_date:today].mean()
                interestlst = series[series > 80].index.tolist()
                sell()
                if len(interestlst) > 0:
                    #moneyToAllocate = 500000/len(interestlst)
                    moneyToAllocate = currentvalue()/(2*len(interestlst))
                    buy(interestlst, moneyToAllocate)


            def main():
                global today
                volume_log = pd.DataFrame(columns=['Date','Current_Value'])
                for ticker in tickers:
                    portfolio[ticker] = 0
                while today <= simend:
                    while not tradingday():
                        today += dt.timedelta(days=1)
                    simulation()
                    currentpvalue = currentvalue()
                    volume_log.loc[volume_log.shape[0]] = [today, currentpvalue]
                    today += dt.timedelta(days=1)

                st.write("\n\nThis is the graph of the portfolio value")

                fig = px.line(        
                        volume_log, #Data Frame
                        x = "Date", #Columns from the data frame
                        y = "Current_Value",
                        title = "Volume Strategy"
                    )
                fig.update_traces(line_color = "green")
                st.plotly_chart(fig)


                length = len(volume_log) - 1
                st.write("With this method, the portfolio was worth {} on {} and today the portfolio is worth: ${}.".format(initial_money, start_date_f, volume_log['Current_Value'][length]))

                performance_volume = (((volume_log['Current_Value'][length])/initial_money)-1)*100
                st.write("This is a fluctuation of {}% over the period.".format(performance_volume))

                volume_log = pd.DataFrame(transactionlog)
                volume_log_str = pd.DataFrame.to_string(volume_log)
                if st.download_button('Download Transaction File', volume_log_str, 'Daily_Intervals_Sectors.txt'):
                    st.write('Thanks for downloading!')

                volume_log['Positive_return']=np.select([volume_log['profit']>0 ,(volume_log['profit']==0) & (volume_log.type=='buy'),
                            (volume_log['profit']==0) & (volume_log.type=='sell'),volume_log['profit']<0],[1,None,-1,-1])

                occurences=[]
                tick_prof=[]
                avg_tick_profit=[]
                profitable=[]
                for ticker in tickers:
                    occurence=len(volume_log.loc[volume_log.ticker==ticker])/2
                    occurences.append(occurence)
                    tot_profit=round(volume_log.loc[volume_log.ticker==ticker].profit.sum(),1)
                    tick_prof.append(tot_profit)
                    avg_tick_profit.append(round(tot_profit/occurence,1))
                    if occurence != 0:
                        profitable.append(round(len(volume_log.loc[(volume_log.ticker==ticker)&(volume_log.Positive_return>0)])/occurence,5)*100)
                    else:
                        profitable.append(0)
                volume_stats=pd.DataFrame()
                volume_stats['ticker']=tickers
                volume_stats['occurences']=occurences
                volume_stats['profit_from_ticker']=tick_prof
                volume_stats['avg_profit']=avg_tick_profit
                volume_stats['%_Positive_returns']=profitable

                st.write("Statistics on the Best Sectors strategy:")
                st.dataframe(volume_stats, height=500)

                fig = px.bar(        
                        volume_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "%_Positive_returns",
                        title = "Daily Intervals Strategy Stats - Percentage of positive returns"
                    )
                st.plotly_chart(fig)

                fig = px.bar(        
                        volume_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "profit_from_ticker",
                        title = "Daily Intervals Strategy Stats - profit made from tickers"
                    )
                st.plotly_chart(fig)

            main()
        elif selected == "Market Strategy":
            week_changes = Prices_Weekly
            
            st.write("This is the dataframe this strategy works on.")
            st.dataframe(week_changes)

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

            def tradingday():
                global week_prices, today
                return np.datetime64(today) in list(week_prices.index.values)
                            
            def simulation():
                global today, week_changes, money
                start_date = today - dt.timedelta(days=7)
                interestlst = tickers_simulation
                sell()
                if len(interestlst) > 0:
                    moneyToAllocate = currentvalue()/(len(interestlst))
                    buy(interestlst, moneyToAllocate)

            def main():
                global today
                market_strategy_log = pd.DataFrame(columns=['Date','Current_Value'])
                for ticker in tickers:
                    portfolio[ticker] = 0
                while today <= simend:
                    while not tradingday():
                        today += dt.timedelta(days=1)
                    simulation()
                    currentpvalue = currentvalue()
                    market_strategy_log.loc[market_strategy_log.shape[0]] = [today, currentpvalue]
                    #st.write([today, currentpvalue])
                    today += dt.timedelta(days=7)

                st.write("\n\nThis is the graph of the portfolio value")

                fig = px.line(        
                        market_strategy_log, #Data Frame
                        x = "Date", #Columns from the data frame
                        y = "Current_Value",
                        title = "Best Sectors Strategy"
                    )
                fig.update_traces(line_color = "green")
                st.plotly_chart(fig)


                length = len(market_strategy_log) - 1
                st.write("With this method, the portfolio was worth {} on {} and today the portfolio is worth: ${}.".format(initial_money, start_date_f, market_strategy_log['Current_Value'][length]))

                performance_best_sectors = (((market_strategy_log['Current_Value'][length])/initial_money)-1)*100
                st.write("This is a fluctuation of {}% over the period.".format(round(performance_best_sectors, 3)))

                market_strategy_log = pd.DataFrame(transactionlog)
                market_strategy_log_str = pd.DataFrame.to_string(market_strategy_log)
                if st.download_button('Download Transaction File', market_strategy_log_str, 'Market Strategy.txt'):
                    st.write('Thanks for downloading!')
                st.write("")

                market_strategy_log['Positive_return']=np.select([market_strategy_log['profit']>0 ,(market_strategy_log['profit']==0) & (market_strategy_log.type=='buy'),
                                 (market_strategy_log['profit']==0) & (market_strategy_log.type=='sell'),market_strategy_log['profit']<0],[1,None,-1,-1])

                occurences=[]
                tick_prof=[]
                avg_tick_profit=[]
                profitable=[]
                for ticker in tickers:
                    occurence=len(market_strategy_log.loc[market_strategy_log.ticker==ticker])/2
                    occurences.append(occurence)
                    tot_profit=round(market_strategy_log.loc[market_strategy_log.ticker==ticker].profit.sum(),1)
                    tick_prof.append(tot_profit)
                    avg_tick_profit.append(round(tot_profit/occurence,1))
                    if occurence > 0:
                        profitable.append(round(len(market_strategy_log.loc[(market_strategy_log.ticker==ticker)&(market_strategy_log.Positive_return>0)])/occurence,5)*100)
                    else:
                        profitable.append(0)
                market_strategy_stats=pd.DataFrame()
                market_strategy_stats['ticker']=tickers
                market_strategy_stats['occurences']=occurences
                market_strategy_stats['profit_from_ticker']=tick_prof
                market_strategy_stats['avg_profit']=avg_tick_profit
                market_strategy_stats['%_Positive_returns']=profitable

                st.write("Statistics on the Market Strategy:")
                st.dataframe(market_strategy_stats, height=500)

                fig = px.bar(        
                        market_strategy_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "%_Positive_returns",
                        title = "Market Strategy Stats - Percentage of positive returns"
                    )
                st.plotly_chart(fig)

                fig = px.bar(        
                        market_strategy_stats, #Data Frame
                        x = "ticker", #Columns from the data frame
                        y = "profit_from_ticker",
                        title = "Market Strategy Stats - profit made from tickers"
                    )
                st.plotly_chart(fig)

            main()
        elif selected == "Interval Strategy Daily":
            st.write("This strategy is similar to the Intervals Strategy Weekly.")
            st.write("Due to technological limitations, we are unable to run this strategy through Streamlit, but you can see the code by ticking the checkbox below.")
            
            if st.checkbox('Show code'):
                st.code("""
                Prices_Daily = pd.read_csv('https://raw.githubusercontent.com/MosheLubliner/FinanceProject/main/Sectors_Prices_Daily.csv', index_col='Date')
                Prices_Daily2 = yf.download(tickers, start=start, end=end, interval='1d')['Adj Close']
                Prices_Daily['Date'] = pd.to_datetime(Prices_Daily.index)
                Prices_Daily.set_index('Date',inplace=True)
                Prices_Daily2['Date'] = pd.to_datetime(Prices_Daily2.index)
                Prices_Daily2.set_index('Date',inplace=True)
                Frames_Prices_Daily = [Prices_Daily, Prices_Daily2]
                Prices_Daily = pd.concat(Frames_Prices_Daily)

                day_prices = Prices_Daily
                tickers = ['XLK', 'XLE', 'XLF', 'XLV', 'XLRE', 'XLB', 'XLY', 'XLP', 'XLU', 'XLI', 'IYZ']
                for ticker in tickers:
                    if ticker not in tickers_simulation:
                        day_prices = day_prices.drop(columns=[ticker])
                day_prices = day_prices[(day_prices.index >= start_date_f) & (day_prices.index <= end_date_f)]
                
                day_changes=day_prices.pct_change()*100
                nxt_d_chg=day_changes.shift(-1)

                st.write("This is the dataframe this strategy works on.")
                st.dataframe(nxt_d_chg)

                def transaction(id, ticker, amount, price, type,profit):
                    global transactionid
                    if type == "buy":
                        exp_date = today + dt.timedelta(days=1)
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

                def tradingday():
                    global day_prices, today
                    return np.datetime64(today) in list(day_prices.index.values)

                def simulation():
                    global today, day_changes, nxt_d_chg, money, tickers
                    start_date = today - dt.timedelta(days=7)
                    n=0.1
                    d={}
                    for ticker in tickers:
                        val=day_changes[ticker].loc[str(today)]
                        date_logic=day_changes.index<str(today)
                        exp_n=nxt_d_chg[ticker].loc[date_logic& (day_changes[ticker]>val-n)&(day_changes[ticker]<val+n)].mean()
                        std_n=nxt_d_chg[ticker].loc[date_logic& (day_changes[ticker]>val-n)&(day_changes[ticker]<val+n)].std()
                        if std_n != 0:
                            sharp=exp_n/std_n
                        else:
                            sharp=0
                        d[ticker]=sharp
                    interestlst = []
                    interestlst.append(max(d, key=d.get))
                    sell()
                    if len(interestlst) > 0:
                        #moneyToAllocate = 500000/len(interestlst)
                        moneyToAllocate = currentvalue()/(len(interestlst))
                        buy(interestlst, moneyToAllocate)


                def main():
                    global today
                    daily_interval_log = pd.DataFrame(columns=['Date','Current_Value'])
                    for ticker in tickers:
                        portfolio[ticker] = 0
                    while today <= simend:
                        while not tradingday():
                            today += dt.timedelta(days=1)
                        simulation()
                        currentpvalue = currentvalue()
                        daily_interval_log.loc[daily_interval_log.shape[0]] = [today, currentpvalue]
                        today += dt.timedelta(days=1)

                    st.write("\n\nThis is the graph of the portfolio value")

                    fig = px.line(        
                            daily_interval_log, #Data Frame
                            x = "Date", #Columns from the data frame
                            y = "Current_Value",
                            title = "Daily Interval Strategy"
                        )
                    fig.update_traces(line_color = "green")
                    st.plotly_chart(fig)


                    length = len(daily_interval_log) - 1
                    st.write("With this method, the portfolio was worth {} on {} and today the portfolio is worth: ${}.".format(initial_money, start_date_f, daily_interval_log['Current_Value'][length]))

                    performance_daily_interval = (((daily_interval_log['Current_Value'][length])/initial_money)-1)*100
                    st.write("This is a fluctuation of {}% over the period.".format(performance_daily_interval))

                    daily_interval_log = pd.DataFrame(transactionlog)
                    daily_interval_log_str = pd.DataFrame.to_string(daily_interval_log)
                    if st.download_button('Download Transaction File', daily_interval_log_str, 'Daily_Intervals_Sectors.txt'):
                        st.write('Thanks for downloading!')

                    daily_interval_log['Positive_return']=np.select([daily_interval_log['profit']>0 ,(daily_interval_log['profit']==0) & (daily_interval_log.type=='buy'),
                                    (daily_interval_log['profit']==0) & (daily_interval_log.type=='sell'),daily_interval_log['profit']<0],[1,None,-1,-1])

                    occurences=[]
                    tick_prof=[]
                    avg_tick_profit=[]
                    profitable=[]
                    for ticker in tickers:
                        occurence=len(daily_interval_log.loc[daily_interval_log.ticker==ticker])/2
                        occurences.append(occurence)
                        tot_profit=round(daily_interval_log.loc[daily_interval_log.ticker==ticker].profit.sum(),1)
                        tick_prof.append(tot_profit)
                        avg_tick_profit.append(round(tot_profit/occurence,1))
                        if occurence > 0:
                        profitable.append(round(len(best_sectors_log.loc[(best_sectors_log.ticker==ticker)&(best_sectors_log.Positive_return>0)])/occurence,5)*100)
                    else:
                        profitable.append(0)
                    daily_interval_stats=pd.DataFrame()
                    daily_interval_stats['ticker']=tickers
                    daily_interval_stats['occurences']=occurences
                    daily_interval_stats['profit_from_ticker']=tick_prof
                    daily_interval_stats['avg_profit']=avg_tick_profit
                    daily_interval_stats['%_Positive_returns']=profitable

                    st.write("Statistics on the Best Sectors strategy:")
                    st.dataframe(daily_interval_stats, height=500)

                    fig = px.bar(        
                            daily_interval_stats, #Data Frame
                            x = "ticker", #Columns from the data frame
                            y = "%_Positive_returns",
                            title = "Daily Intervals Strategy Stats - Percentage of positive returns"
                        )
                    st.plotly_chart(fig)

                    fig = px.bar(        
                            daily_interval_stats, #Data Frame
                            x = "ticker", #Columns from the data frame
                            y = "profit_from_ticker",
                            title = "Daily Intervals Strategy Stats - profit made from tickers"
                        )
                    st.plotly_chart(fig)

                main()
                """
                )
except URLError as e:
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
