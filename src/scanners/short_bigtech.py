import datetime, config, pandas, sys
from numpy import percentile
#from alpaca_trade_api.stream import Stream
from alpaca_trade_api.rest import REST, TimeFrame#, TimeFrameUnit

pandas.set_option('display.max_rows', None)

trade_orders = []
# 打開trading log文件, 拿到所有現有的trade order
df = pandas.read_csv('trading_log_big_tech.csv', index_col = 0, )
#print (df)

# 保存所有現有和現時開單的記錄
def save_df(df, trading_order):
    df = df.append(trading_order, ignore_index=True, sort=False)
    #print (f"PD = {df}")
    return df



api = REST(key_id=config.API_KEY, secret_key=config.SECRET_KEY, base_url=config.BASE_URL)

# GAP UP/DOWN %
gap_percent = 3

# 睇下今日有無開巿
# if not api.get_clock().is_open:
#     sys.exit("\n未開巿\n\n")
# else:
 #    print("\n已開巿\n\n")


# 拿最新的bars
#bars = api.get_bars(config.QQQ_SYMBOLS, TimeFrame.Day, config.START_DATE, config.TODAY).df
bars = api.get_bars(config.QQQ_SYMBOLS, TimeFrame.Day, config.START_DATE, config.YESTERDAY).df
#print(bars)

# 把之前的收巿價拿到同一行
bars['previous_close'] = bars['close'].shift(1)

# 本來係用previous_close, 係教學度, 但我認為係用close先岩, 
# 因為我地呢度拎唔到TODAY, 但真係做時要拎返TODAY 同PREVIOUS CLOSE
bars['ma'] = bars['close'].rolling(config.MOVING_AVERAGE_DAYS).mean()
#print(bars)

# 只拿最新的日字, 這裏是拿yesterday, 如果有比錢就拿today
#filtered = bars[bars.index.strftime('%Y-%m-%d') == config.TODAY.isoformat()].copy()
filtered = bars[bars.index.strftime('%Y-%m-%d') == config.YESTERDAY.isoformat()].copy()
filtered['percent'] = ((filtered['open'] - filtered['previous_close']) / filtered['previous_close']) *100
downgaps = filtered[filtered['percent'] < -abs(gap_percent)] # 設定數值
upgaps = filtered[filtered['percent'] > gap_percent]

#print(filtered)
#print('\n\n\nSTOCK PRICE DOWN UP > 1% \n')
#print(downgaps)
#print('\n\n\nSTOCK PRICE MOVE UP > 1% \n')
#print(upgaps)

# filter downgaps below moving average 出現gap之外, 仲穿埋20ma
downgaps_below_ma = downgaps[downgaps['open'] < downgaps['ma']]
upgaps_above_ma = upgaps[upgaps['open'] > upgaps['ma']]

print(f'\n\n\n今天的Big Tech股票價格下跌超過 > {gap_percent}%, 更向下跌穿20天平均線\n')
print(downgaps_below_ma)

# 如果在清單中, 這些股票下穿20天線後, 今天比昨天下跌了超過了 2 + 2 % 就用巿價去買跌, 這裏是清單
market_order_symbols = downgaps_below_ma[downgaps_below_ma['percent'] < -abs(gap_percent)]['symbol'].tolist()

# 如果在清單中, 這些股票下穿20天線後, 今天比昨天下跌了超過了 2 % 就用巿價去買跌, 這裏是清單
# 唔做呢個
#bracket_order_symbols = downgaps_below_ma[downgaps_below_ma['percent'] < -abs(gap_percent)]['symbol'].tolist()


#print (market_order_symbols)
#print (bracket_order_symbols)

# 同道理可以做買升

# 如果唔夠錢買一手, 就remove
for symbol in market_order_symbols:# 在清單中的每隻股票
    open_price = downgaps[downgaps.symbol == symbol]['open'].iloc[-1]
    quantity = config.ORDER_DOLLAR_SIZE // open_price
    if quantity == 0:
        market_order_symbols.remove(symbol)

print(f'\n\n\n今天的股票價格下跌超過 > {gap_percent}%, 更向下跌穿20天平均線, 而每股價錢少於 {config.ORDER_DOLLAR_SIZE} 美元\n')
print (market_order_symbols)



# 計算買賣
for symbol in market_order_symbols:# 在清單中的每隻股票

    open_price = downgaps[downgaps.symbol == symbol]['open'].iloc[-1]
    quantity = config.ORDER_DOLLAR_SIZE // open_price

    now = datetime.datetime.now()
    date_string = now.strftime("%Y年%m月%d日-%H時%M分")

    print (f"\n準備賣出股票為: {symbol} 買入數量為: {quantity}股, 價錢為: {open_price}, \n賣出時間為: {date_string}\n\n")
    

    
    
    # API 的賣出動作, 呢個一定要係早上開始, 唔係佢唔會行, 如果要手動, 寫過一個function
    try:
            order = api.submit_order(symbol, quantity, 'sell', 'market')
            now = datetime.datetime.now()
            date_string = now.strftime("%Y年%m月%d日-%H時%M分")
            print("成功以巿價賣出, ORDER ID 為: {}\n\n".format(order.id))
            trading_order = {"賣出時間" : date_string, "股票代號":symbol, "賣出股數": quantity, "賣出價錢": open_price, "總價": float(quantity * open_price), "ORDER ID" :order.id}
            df = save_df(df, trading_order)
    except Exception as e:
            print("出現錯誤 {}".format(e))

df.to_csv('trading_log_big_tech.csv', encoding="utf-8_sig")

# quotes = api.get_latest_quotes(bracket_order_symbols)
# print (quotes)

#賣出限價單
# for symbol in bracket_order_symbols: #每一個在限價清單中的股票
#     quantity = config.ORDER_DOLLAR_SIZE // quotes[symbol].bp
#     take_profit = round(quotes[symbol].bp * 0.99, 2) #小數點後兩個位
#     stop_price = round(quotes[symbol].bp * 1.01, 2)
#     stop_limit_price = round(quotes[symbol].bp * 1.02, 2)

#     print("{} shorting {} {} at {}".format(datetime.datetime.now().isoformat(), quantity, symbol, quotes[symbol].bp))
#     print(f"\n準備賣出股票為: {symbol} 買入數量為: {quantity}股, 價錢為: {quotes[symbol].bp}, \n賣出時間為: {datetime.datetime.now().isoformat()}\n\n")


#     try:
#         order = api.submit_order(symbol, quantity, 'sell', 
#                                     order_class='bracket', 
#                                     take_profit={
#                                         'limit_price': take_profit
#                                     }, 
#                                     stop_loss={
#                                         'stop_price': stop_price, 
#                                         'limit_price': stop_limit_price
#                                     })
#         print("成功以限價{}賣出, ORDER ID 為: {}".format(quotes[symbol].bp, order.id))
#     except Exception as e:
#         print("出現錯誤 {}".format(e))