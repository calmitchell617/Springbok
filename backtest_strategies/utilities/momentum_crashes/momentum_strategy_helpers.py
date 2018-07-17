from zipline.api import order_target_percent, order_target

def get_longs(context):

    if context.market_type == 'bull':
        return context.output.sort_values(['lagged_returns'])[-100:]
    else:
        return context.output.sort_values(['lagged_returns'])[:100]

def get_shorts(context):
    if context.market_type == 'bear':
        return context.output.sort_values(['lagged_returns'])[:100]
    else:
        return context.output.sort_values(['lagged_returns'])[-100:]

def portfolio_logic(context):
    longs_to_remove = []

    for asset in context.longs_portfolio:  # search portfolio for positions to close out
        if asset not in context.longs.index:
            longs_to_remove.append(asset)
            order_target(asset, 0)

    for asset in context.longs.index:  # search context.longs for stocks to add to portfolio
        order_target_percent(asset, .00025)
        if asset not in context.longs_portfolio:
            context.longs_portfolio[asset] = True


    for key in longs_to_remove:
        context.longs_portfolio.pop(key)

    shorts_to_remove = []

    for asset in context.shorts_portfolio:  # search portfolio for positions to close out
        if asset not in context.shorts.index:
            shorts_to_remove.append(asset)
            order_target(asset, 0)

    for asset in context.shorts.index:  # search context.shorts for stocks to add to portfolio
        if asset not in context.shorts_portfolio:
            context.shorts_portfolio[asset] = True
            order_target_percent(asset, -0.00025)

    for key in shorts_to_remove:
        context.shorts_portfolio.pop(key)