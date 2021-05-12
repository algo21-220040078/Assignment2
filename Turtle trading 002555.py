
#海归交易法则
# 2018-01-01 到 2020-04-31, ￥1000000, 分钟

def initialize(context):
    set_params()       
    set_variables()     
    set_backtest()      
    
#设置策略参数
def set_params():
    g.security = '002555.XSHE'
    # 系统1入市的trailing date
    g.short_in_date = 20
    # 系统2入市的trailing date
    g.long_in_date = 55
    # 系统1 exiting market trailing date
    g.short_out_date = 10
    # 系统2 exiting market trailing date
    g.long_out_date = 20
    # g.dollars_per_share是标的股票每波动一个最小单位，1手股票的总价格变化量。
    g.dollars_per_share = 1
    # 可承受的最大损失率
    g.loss = 0.1
    # 若超过最大损失率，则调整率为：
    g.adjust = 0.8
    # 计算N值的天数
    g.number_days = 20
    # 最大允许单元
    g.unit_limit = 4
    # 系统1所配金额占总金额比例
    g.ratio = 0.8
    
#设置中间变量
def set_variables():
    # 初始单元
    g.unit = 1000
    # A list storing info of N
    g.N = []
    # Record the number of days for this trading system
    g.days = 0
    # 系统1的突破价格
    g.break_price1 = 0
    # 系统2的突破价格
    g.break_price2 = 0
    # 系统1建的仓数
    g.sys1 = 0
    # 系统2建的仓数
    g.sys2 = 0
    # 系统1执行且系统2不执行
    g.system1 = True

#设置回测条件
def set_backtest():
    set_benchmark(g.security)
    set_option('use_real_price',True)
    log.set_level('order','error') 


def before_trading_start(context):
    set_slip_fee(context) 


#手续费
def set_slip_fee(context):
    # 将滑点设置为0
    set_slippage(FixedSlippage(0)) 
    dt=context.current_dt
    if dt>datetime.datetime(2013,1, 1):
        set_commission(PerTrade(buy_cost=0.0003, sell_cost=0.0013, min_cost=5)) 
        
    elif dt>datetime.datetime(2011,1, 1):
        set_commission(PerTrade(buy_cost=0.001, sell_cost=0.002, min_cost=5))
            
    elif dt>datetime.datetime(2009,1, 1):
        set_commission(PerTrade(buy_cost=0.002, sell_cost=0.003, min_cost=5))
                
    else:
        set_commission(PerTrade(buy_cost=0.003, sell_cost=0.004, min_cost=5))


# 按分钟回测
def handle_data(context, data):
    dt = context.current_dt # 当前日期
    current_price = data[g.security].price # 当前价格N
    if dt.hour==9 and dt.minute==30:
        g.days += 1
        calculate_N() #计算N的值
    if g.days > g.number_days:
        # 当前持有的股票和现金的总价值
        value = context.portfolio.portfolio_value
        cash = context.portfolio.cash 
        if g.sys1 == 0 and g.sys2 == 0:
            # 若损失率大于g.loss，则调整（减小）可持有现金和总价值
            if value < (1-g.loss)*context.portfolio.starting_cash:
                cash *= g.adjust
                value *= g.adjust
                
        dollar_volatility = g.dollars_per_share*(g.N)[-1]
        g.unit = value*0.01/dollar_volatility

        # 系统1的操作
        g.system1 = True
        if g.sys1 == 0:
            market_in(current_price, g.ratio*cash, g.short_in_date)
        else:
            stop_loss(current_price)
            market_add(current_price, g.ratio*cash, g.short_in_date)    
            market_out(current_price, g.short_out_date)

        # 系统2的操作
        g.system1 == False
        if g.sys2==0:
            market_in(current_price, (1-g.ratio)*cash, g.long_in_date)
        else:
            stop_loss(current_price)
            market_add(current_price, (1-g.ratio)*cash, g.long_in_date)
            market_out(current_price, g.long_out_date)   
  


def calculate_N():
    if g.days <= g.number_days:
        price = attribute_history(g.security, g.days, '1d',('high','low','pre_close'))
        lst = []
        for i in range(0, g.days):
            h_l = price['high'][i]-price['low'][i]
            h_c = price['high'][i]-price['pre_close'][i]
            c_l = price['pre_close'][i]-price['low'][i]
            True_Range = max(h_l, h_c, c_l)
            lst.append(True_Range)
        current_N = np.mean(np.array(lst))
        (g.N).append(current_N)
        
#大于20天
    else:
        price = attribute_history(g.security, 1, '1d',('high','low','pre_close'))
        h_l = price['high'][0]-price['low'][0]
        h_c = price['high'][0]-price['pre_close'][0]
        c_l = price['pre_close'][0]-price['low'][0]
        True_Range = max(h_l, h_c, c_l)
        current_N = (True_Range + (g.number_days-1)*(g.N)[-1])/g.number_days
        (g.N).append(current_N)



# 入市
#  分为两部分，按照两个系统执行

def market_in(current_price, cash, in_date):
    price = attribute_history(g.security, in_date, '1d', ('close'))
    if current_price > max(price['close']):
        num_of_shares = cash/current_price
        if num_of_shares >= g.unit:
            print ("买入")
            print (current_price)
            print (max(price['close']))
            if g.system1 == True:
                if g.sys1 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys1 += int(g.unit)
                    g.break_price1 = current_price
            else:
                if g.sys2 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys2 += int(g.unit)
                    g.break_price2 = current_price


# 加仓函数
def market_add(current_price, cash, in_date):
    if g.system1 == True:
        break_price=g.break_price1
    else:
        break_price=g.break_price2
    # 每上涨0.5N，加仓一个单元
    if current_price >= break_price + 0.5*(g.N)[-1]: 
        num_of_shares = cash/current_price
        # 加仓
        if num_of_shares >= g.unit: 
            print ("加仓")
            print (g.sys1)
            print (g.sys2)
            print (current_price)
            print (break_price + 0.5*(g.N)[-1])
       
            if g.system1 == True:
                if g.sys1 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys1 += int(g.unit)
                    g.break_price1 = current_price
            else:
                if g.sys2 < int(g.unit_limit*g.unit):
                    order(g.security, int(g.unit))
                    g.sys2 += int(g.unit)
                    g.break_price2 = current_price


# 离场函数
def market_out(current_price, out_date):
    price = attribute_history(g.security, out_date, '1d', ('close'))
    # 若当前价格低于前out_date天的收盘价的最小值, 则卖掉所有持仓
    if current_price < min(price['close']):
        print ("离场")
        print (current_price)
        print (min(price['close']))
        if g.system1 == True:
            if g.sys1>0:
                order(g.security, -g.sys1)
                g.sys1 = 0
        else:
            if g.sys2>0:
                order(g.security, -g.sys2)
                g.sys2 = 0


# 止损函数
def stop_loss(current_price):
    if g.system1 == True:
        break_price = g.break_price1
    else:
        break_price = g.break_price2
    if current_price < (break_price - 2*(g.N)[-1]):
        print ("止损")
        print (current_price)
        print (break_price - 2*(g.N)[-1])
        if g.system1 == True:
            order(g.security, -g.sys1)
            g.sys1 = 0  
        else:
            order(g.security, -g.sys2)
            g.sys2 = 0