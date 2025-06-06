import datetime, config, sys
#from alpaca_trade_api.stream import Stream
from alpaca_trade_api.rest import REST, TimeFrame#, TimeFrameUnit
import pandas

trade_orders = []
# 打開trading log文件, 拿到所有現有的trade order
df = pandas.read_csv('trading_log_small_caps.csv', index_col = 0, )
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
#if not api.get_clock().is_open:
    #sys.exit("\n未開巿\n\n")
#else:
    #print ("\n已開巿\n\n")


# 拿最新的bars
bars = api.get_bars(config.IWM_SYMBOLS, TimeFrame.Day, config.START_DATE, config.YESTERDAY).df #呢度要改返做today

# 把之前的收巿價拿到同一行
bars['previous_close'] = bars['close'].shift(1)

# 本來係用previous_close, 係教學度, 但我認為係用close先岩, 
# 因為我地呢度拎唔到TODAY, 但真係做時要拎返TODAY 同PREVIOUS CLOSE
bars['ma'] = bars['close'].rolling(config.MOVING_AVERAGE_DAYS).mean() #呢度改返做close, 但真實的話要用previous close, 因為今日既close係無既

#print(bars)
# 只拿最新的日字, 這裏是拿yesterday, 如果有比錢就拿today
filtered = bars[bars.index.strftime('%Y-%m-%d') == config.YESTERDAY.isoformat()].copy()
filtered['percent'] = ((filtered['open'] - filtered['previous_close']) / filtered['previous_close']) *100
downgaps = filtered[filtered['percent'] < -abs(gap_percent)] # 設定數值
upgaps = filtered[filtered['percent'] > gap_percent]

#print(filtered)
#print('\n\n\nSTOCK PRICE DOWN UP > 1% \n')
#print(downgaps)
#print('\n\n\nSTOCK PRICE MOVE UP > 1% \n')
#print(upgaps)

# filter downgaps below moving average 出現gap之外, 但無穿20ma
downgaps_above_ma = downgaps[downgaps['open'] > downgaps['ma']]
print(f'\n\n\n今天的Small Caps股票價格下跌超過 > {gap_percent}%, 但不低於20天平均的股票為: \n')
print (downgaps_above_ma)

market_order_symbols = downgaps_above_ma[downgaps_above_ma['percent'] < -abs(gap_percent)]['symbol'].tolist() #巿價單 呢D 路 3 - 3.5
#trailing_stop_order_symbols = downgaps_above_ma[downgaps_above_ma['percent'] < 0.965]['symbol'].tolist() # 限價單, 呢D 跌好多

print(f'\n\n\n今天的Small Caps股票價格下跌超過 > {gap_percent}%, 但不低於20天平均的股票為: \n')
#print (market_order_symbols)

# 如果唔夠錢買一手, 就remove
for symbol in market_order_symbols:# 在清單中的每隻股票
    open_price = downgaps[downgaps.symbol == symbol]['open'].iloc[-1]
    quantity = config.ORDER_DOLLAR_SIZE // open_price
    if quantity == 0:
        market_order_symbols.remove(symbol)
print (market_order_symbols)

# 計算買賣
for symbol in market_order_symbols:

    open_price = downgaps[downgaps.symbol == symbol]['open'].iloc[-1]
    quantity = config.ORDER_DOLLAR_SIZE // open_price

    now = datetime.datetime.now()
    date_string = now.strftime("%Y年%m月%d日-%H時%M分")

    print (f"\n準備買入股票為: {symbol} 買入數量為: {quantity}股, 價錢為: {open_price}, \n買入時間為: {date_string}\n\n")
    

    # API 賣出動作
    try:
        order = api.submit_order(symbol, quantity, 'buy', 'limit', limit_price=round(open_price, 2))
        now = datetime.datetime.now()
        date_string = now.strftime("%Y年%m月%d日-%H時%M分")
        print("成功以巿價買入, ORDER ID 為: {}\n\n".format(order.id))
        trading_order = {"買入時間" : date_string, "股票代號":symbol, "買入股數": quantity, "買入價錢": open_price, "總價": float(quantity * open_price), "ORDER ID" :order.id}
        df = save_df(df, trading_order)
    except Exception as e:
        print("出現錯誤 {}".format(e))

df.to_csv('trading_log_small_caps.csv', encoding="utf-8_sig")


# trailing_stop 例子
# quotes = api.get_latest_quotes(trailing_stop_order_symbols)

# for symbol in trailing_stop_order_symbols:
#     quantity = config.ORDER_DOLLAR_SIZE // quotes[symbol].bp
#     print("{} buying {} {} at {}".format(datetime.datetime.now().isoformat(), quantity, symbol, quotes[symbol].bp))

#     try:
#         order = api.submit_order(symbol, quantity, 'buy', 'trailing_stop', trail_percent=1.0)
#         print("successfully submitted trailing stop order with order_id {}".format(order.id))
#     except Exception as e:
#         print("problem submitting above order - {}".format(e))