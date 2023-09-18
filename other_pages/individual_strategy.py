import streamlit as st
import yfinance as yf
import numpy as np 
import matplotlib.pyplot as plt
import datetime as dt
import talib as ta 
import pandas as pd
import yfinance as yf
import sys
from backtesting import Strategy, Backtest
from backtesting.test import SMA
from datetime import date
import plotly.graph_objects as go
from st_pages import Page, show_pages
sys.path.insert(0, './other_pages')
from backtest import MACD, MeanReversion, SwingTrading, RsiOscillator

# pick security and time frame

show_pages(
    [
        Page("streamlit_app.py", "Home"),
        Page("other_pages/individual_strategy.py", "Backtest")
    ]
)

# pick ticker and time interval
ticker_options = pd.read_excel('indicators.xlsx')

options = ticker_options['tickers']

ticker = st.selectbox(
    'Which Security are we lookin at losing money on today?',
    (options))


lookback_duration = st.number_input("How many calendar days of history do you want to chart and test?", min_value=60, max_value=365, step=7)


# get data based on time interval until today
today = date.today() - dt.timedelta(lookback_duration)
one_month_lag_date = today.strftime('%Y-%m-%d')

stock = yf.download(ticker, start=one_month_lag_date)[
    ["Open", "High", "Low", "Close", "Volume"]
]

# Backtesting section 

def optim_func(series):
    if series['# Trades'] < 10:
        return -1
    return series["Equity Final [$]"] / series ["Exposure Time [%]"]


# select strategy picklist 
strategy = st.selectbox(
    'Strategy to test?',
    ('MACD','MeanReversion','SwingTrading','RsiOscillator'))

if strategy == 'MACD':
    with st.spinner("testing.."):
        bt = Backtest(stock, MACD, cash=100000, commission=0.002)
        stats = bt.optimize(position_size = range(25,100,5), maximize = optim_func, max_tries = 50)
        st.write("Trade(s) Placed:")
        st.dataframe(stats['_trades'][['Size', 'EntryBar', 'ExitBar',  'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct', 'EntryTime', 'ExitTime']])
        st.write("Backtesting Stats:")
        st.dataframe(stats)

elif strategy == 'MeanReversion':
    with st.spinner("testing.."):
        bt = Backtest(stock, MeanReversion, cash=100000, commission=0.002)
        stats = bt.optimize(position_size = range(25,100,5), maximize = optim_func, max_tries = 50)
        st.write("Trade(s) Placed:")
        st.dataframe(stats['_trades'][['Size', 'EntryBar', 'ExitBar',  'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct', 'EntryTime', 'ExitTime']])
        st.write("Backtesting Stats:")
        st.dataframe(stats)

elif strategy == 'SwingTrading':
    with st.spinner("testing.."):
        bt = Backtest(stock, SwingTrading, cash=100000, commission=0.002, trade_on_close=True)
        stats = bt.optimize(position_size = range(25,100,5), maximize = optim_func, max_tries = 50)
        st.write("Trade(s) Placed:")
        st.dataframe(stats['_trades'][['Size', 'EntryBar', 'ExitBar',  'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct', 'EntryTime', 'ExitTime']])
        st.write("Backtesting Stats:")
        st.dataframe(stats)

elif strategy == 'RsiOscillator':
    with st.spinner("testing.."):
        bt = Backtest(stock, RsiOscillator, cash=100000, commission=0.002)
        stats = bt.optimize(position_size = range(25,100,5), maximize = optim_func, max_tries = 50)
        st.write("Trade(s) Placed:")
        st.dataframe(stats['_trades'][['Size', 'EntryBar', 'ExitBar',  'EntryPrice', 'ExitPrice', 'PnL', 'ReturnPct', 'EntryTime', 'ExitTime']])
        st.write("Backtesting Stats:")
        st.dataframe(stats)

stock = stock.reset_index()

# candlestick plot 

fig = go.Figure(data=[go.Candlestick(x=stock.index,
                                     open=stock['Open'],
                                     high=stock['High'],
                                     low=stock['Low'],
                                     close=stock['Close'])])

st.plotly_chart(fig)


lower_bound, upper_bound = st.select_slider(
    'Select RSI bounds',
    options=range(10,95,5),
    value=(RsiOscillator.lower_bound, RsiOscillator.upper_bound))

# Calculate the RSI indicator 
macd, signal, hist = ta.MACD(stock['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
daily_rsi = ta.RSI(stock['Close'], 14)
stock['RSI'] = daily_rsi

# Add the MACD indicator to the DataFrame
stock['MACD'] = macd
stock['signal'] = signal
stock['hist'] = hist

stock['Date'] = stock['Date'].dt.tz_localize(None) 
stock['Date'] = stock['Date'].apply(lambda x: pd.Timestamp(x))
stock['Date'] = stock['Date'].dt.date
stock = stock.set_index('Date')


# Plot RSI
fig_rsi, ax_rsi= plt.subplots()
plt.xticks(rotation=90)
ax_rsi.plot(stock['RSI'], label='RSI')
ax_rsi.set_xticklabels(labels=stock.index, fontdict={"fontsize": 8})
plt.legend()
ax_rsi.axhline(y=lower_bound, color='red', linestyle='--')
ax_rsi.axhline(y=upper_bound, color='green', linestyle='--')
st.pyplot(fig_rsi)

# Plot MACD
fig_macd, ax_macd= plt.subplots()
plt.xticks(rotation=90)
stock = stock[stock['MACD'].notna()]
ax_macd.plot(stock['MACD'], label='MACD')
ax_macd.plot(stock['signal'], label='Signal')
ax_macd.bar(stock.index, stock['hist'], color = 'green', tick_label = stock.index)
ax_macd.set_xticklabels(labels=stock.index, fontdict={"fontsize": 8})
plt.legend()
ax_macd.axhline(y=0, color='black', linestyle='--')
st.pyplot(fig_macd)



