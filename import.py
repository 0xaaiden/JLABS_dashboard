import glob
import pandas as pd

all_files = glob.glob("trades_data/order_data/*.csv")
all_files.sort()
li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)
frame = pd.concat(li, axis=0, ignore_index=True)
#Choose moverTrades only
frame = frame[frame["priceChange"] == True]

orders = frame.to_csv("trades_data/orders_updated.csv", index=False)