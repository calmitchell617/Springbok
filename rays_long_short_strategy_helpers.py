from zipline.api import order_target_percent, order_target

def get_longs(filtered_by_cap):
    pe1_longs = filtered_by_cap.sort_values(['pe1'])[:1000]  # filter 1000 stocks with lowest pe ratios
    eg_longs = pe1_longs.sort_values(['earnings_growth'])[-500:]  # filter 500 stocks with highest earning growth
    return eg_longs.sort_values(['de'])[:100]  # filter top 100 stocks by lowest debt equity ratio


def get_shorts(filtered_by_cap):
    pe1_shorts = filtered_by_cap.sort_values(['pe1'])[-1000:]  # same thing but backwards for shorts
    eg_shorts = pe1_shorts.sort_values(['earnings_growth'])[:500]
    return eg_shorts.sort_values(['de'])[-100:]

def portfolio_logic(context):
    longs_to_remove = []

    for asset in context.longs_portfolio:  # search portfolio for positions to close out
        if asset not in context.longs.index:
            longs_to_remove.append(asset)
            order_target(asset, 0)

    for asset in context.longs.index:  # search context.longs for stocks to add to portfolio
        if asset not in context.longs_portfolio:
            context.longs_portfolio[asset] = True
            order_target_percent(asset, .005)

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
            order_target_percent(asset, -0.005)

    for key in shorts_to_remove:
        context.shorts_portfolio.pop(key)
