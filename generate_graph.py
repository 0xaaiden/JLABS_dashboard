# -*- coding: utf-8 -*-
#import libs
import glob
import numpy as np
from itertools import *
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objs import *
from plotly.offline import iplot, init_notebook_mode, plot


#import price data - replace path
data = pd.read_csv("trades_data/binance-BTCUSDT-4h.csv")

#import order data (pls replace path with path to your csv folder containing the csv files for the data)
# path = r'/Users/user/Desktop/trades/csv_data2' # use your path
all_files = glob.glob("trades_data/order_data/*.csv")
all_files.sort()
li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)
frame = pd.concat(li, axis=0, ignore_index=True)
#Choose moverTrades only
frame = frame[frame["priceChange"] == True]

def gen_frame_final(trade_size):
    #create a data frame with a minimum amount for orders executed
    frame_final = frame[(frame["amount"] > trade_size)]
    frame_final.loc[:,"timestamp"] = pd.to_datetime(frame_final.loc[:,"timestamp"]).apply(lambda x: x.replace(tzinfo=None))
    frame_final.reset_index(inplace=True)
    return frame_final

high_r = 60000
low_r = 28000
jump_range = 130
range_prices = list(range(low_r,high_r,jump_range))
trade_sizes = [100000,250000, 500000, 1000000]
liq_levels= {"5x": [0.1632, 0.2466],
            "10x": [0.0867, 0.1069],
            "25x": [0.0338, 0.0370],
            "100x": [0.0049, 0.0051]}

def populate_z(liq_lvl, frame_final, data_gen, sd, ed, z):
    for index in range(1,len(range_prices)):
        lower_end = range_prices[index-1]
        higher_end = range_prices[index]
        range_orders_buy = frame_final[(frame_final["timestamp"] >= data_gen["Timestamp"].min()) & (frame_final["timestamp"] <= data_gen["Timestamp"].max()) & (frame_final["price"] >= lower_end) & (frame_final["price"] <= higher_end) & (frame_final["side"] == "buy")]
        range_orders_sell = frame_final[(frame_final["timestamp"] >= data_gen["Timestamp"].min()) & (frame_final["timestamp"] <= data_gen["Timestamp"].max()) & (frame_final["price"] >= lower_end) & (frame_final["price"] <= higher_end) & (frame_final["side"] == "sell")]
        #buy orders
        range_orders_buy.loc[len(range_orders_buy.index)] = [0,0,0,0,0,0,0,0,pd.to_datetime(data_gen.Timestamp.min()),0]
        range_orders_buy.loc[len(range_orders_buy.index)] = [0,0,0,0,0,0,0,0,pd.to_datetime(data_gen.Timestamp.max()),0]
        resampled_dates_buy = range_orders_buy.resample("4H", on="timestamp").amount.sum()

        #sell orders
        range_orders_sell.loc[len(range_orders_sell.index)] = [0,0,0,0,0,0,0,0,pd.to_datetime(data_gen.Timestamp.min()), 0]
        range_orders_sell.loc[len(range_orders_sell.index)] = [0,0,0,0,0,0,0,0,pd.to_datetime(data_gen.Timestamp.max()), 0]
        resampled_dates_sell = range_orders_sell.resample("4H", on="timestamp").amount.sum()

        #print(resampled_dates_buy, "sell: ", resampled_dates_sell)
        sell_lev = lower_end + lower_end * liq_levels[liq_lvl][1]
        buy_lev = lower_end - lower_end * liq_levels[liq_lvl][0]
        #print("sell lev is: ", sell_lev, buy_lev)


        #print("count non zero values:", np.count_nonzero(resampled_dates_buy), "sell: ", np.count_nonzero(resampled_dates_sell))
        #buy matrix
        if ((np.count_nonzero(resampled_dates_buy) + np.count_nonzero(resampled_dates_sell)) != 0):
            #print('printing this one')
            idx_buy = int(((buy_lev-low_r)/jump_range))
            index_buy = range_prices[idx_buy]
            #print("index_buy;", index_buy, idx_buy)

            idx_sell = int(((sell_lev-low_r)/jump_range))
            #print("index_sell: ", idx_sell)
            #index_sell = range_prices[idx_sell]
            #print("index_sell: ", index_sell, idx_sell)
            #print(len(resampled_dates_buy))
            z[idx_buy,0:len(resampled_dates_buy)] = resampled_dates_buy
            #sell matrix
            z[idx_sell,0:len(resampled_dates_sell)] = resampled_dates_sell
            continue
        #print("skipping this")

def clean_z(z_new, data_gen):
    for idx,row in data_gen.iterrows():
    #print(idx, row)
        lower_bucket = int((row.Low - low_r)/jump_range)
        higher_bucket = int((row.High - low_r)/jump_range)
        #print(lower_bucket, higher_bucket, "timestamp", row.Timestamp)
    
        #delete price data in those buckets
        #idx in index of our timestamp
        for i in range(lower_bucket, higher_bucket+1):
            if (idx == (data_gen.shape[0] - 1)):
                #print("done")
                continue
            #print(z_new[i][idx])
            z_new[i][idx+1:] = z_new[i][idx+1:] - z_new[i][idx]
    return z_new    
    
def generate_fig(ll,ts, sd, ed):
    data_gen = data[(data["Timestamp"] >= sd) & (data["Timestamp"] <= ed)]
    data_gen.reset_index(inplace=True)
    frame_final = gen_frame_final(ts)
    print("1st step done")
    #print(data_gen)
    #generate the z
    dates_ts = data_gen.Timestamp
    z2 = np.zeros((len(range_prices), len(dates_ts)))
    print("2nd step done")
    
    #populate the z
    #print(z2, np.count_nonzero(z2))
    populate_z(ll, frame_final, data_gen, sd, ed, z2)
    print("3rd step done")
    #print(z2, np.count_nonzero(z2))
    z_new2 = np.array([a.cumsum() for a in z2])
    
    #clean z
    z_clean2 = clean_z(z_new2, data_gen)
    print("4th step done")
    
    fig2 = go.Figure(data=go.Heatmap(
        z=z_clean2,
        x=dates_ts,
        y=range_prices,
        colorbar={"title": 'Volume $'},
        colorscale='BuPu'))
    fig2.add_trace(go.Candlestick(x=data_gen['Timestamp'],
                             open=data_gen['Open'],
                             high=data_gen['High'],
                             low=data_gen['Low'],
                             close=data_gen['Close']))


    fig2.update_layout(
        title= {"text": "Liquidations heatmap", "x": 0.05, "xanchor": "left"},
        xaxis=dict(ticks='', showgrid=False, zeroline=False),
        yaxis=dict(ticks='', showgrid=True, zeroline=False),
        xaxis_title="Timeline",
        yaxis_title="Price USD",
        autosize=True,
        height=768,
        hovermode='closest')
    
    return fig2
    
    