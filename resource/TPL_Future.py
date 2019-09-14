# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # context内引入全局变量s1
    context.s1 = "AG1612"
    context.fired = False

    # 初始化时订阅合约行情。订阅之后的合约行情会在handle_bar中进行更新。
    subscribe(context.s1)
    # 实时打印日志
    logger.info("RunInfo: {}".format(context.run_info))


# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass


# 你选择的期货数据更新将会触发此段逻辑，例如日线或分钟线更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    # bar_dict[order_book_id] 可以获取到当前期货合约的bar信息
    # context.portfolio 可以获取到当前投资组合信息
    # 使用buy_open(id_or_ins, amount)方法进行买入开仓操作
    if not context.fired:
        buy_open(context.s1, 1)
        context.fired = True
        # TODO: 开始编写你的算法吧！


# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass
