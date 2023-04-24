import backtrader as bt


# def log_trade()
def log_trade(trade: bt.trade.Trade, digits=5, log_func=print) -> None:
    if not trade.isclosed:
        return

    log_func(
        f"TRADE {trade.ref} CLOSED: gross_pnl = {round(trade.pnl, digits)}, net_pnl = {round(trade.pnlcomm, digits)}."
    )


def log_order(order: bt.order.Order, digits=5, log_func=print) -> None:
    # extract order type
    d_order_type = {
        order.Market: "MKT",
        order.Limit: "LMT",
        order.Stop: "STOP",
        order.StopLimit: "STOPLMT",
    }
    if order.exectype in d_order_type:
        order_type = d_order_type[order.exectype]
    else:
        order_type = ""
        log_func(f"WARNING: UNKNOWN ORDER TYPEL: {order.exectype}")
    direction = "BUY" if order.isbuy() else "SELL"
    partial = "PARTIALLY " if order.status == order.Partial else ""  # order.executed.exbits has partial fill details

    if order.status in [order.Created, order.Submitted]:
        return

    if order.status == order.Accepted:
        log_func(
            f"{direction} {order_type} ORDER ACCEPTED: "
            f"price = {order.created.price}, size = {abs(order.created.size)}, margin = {order.created.margin}."
        )

    elif order.status in [order.Partial, order.Completed]:
        if order.isbuy():
            slippage = round((order.executed.price / order.created.price - 1) * 10000, 1)  # in %%
        else:
            slippage = round((1 - order.executed.price / order.created.price) * 10000, 1)  # in %%
        value = round(abs(order.executed.price * order.executed.size), digits)
        log_func(
            f"{direction} {order_type} ORDER {partial}EXECUTED: "
            f"order_price = {round(order.created.price, digits)}, execute_price = {round(order.executed.price, digits)}, slippage = {slippage} %%, "
            f"size = {abs(order.executed.size)}, value = {value}, "
            f"margin = {order.executed.margin}, commission = {round(order.executed.comm, digits)}."
        )

    elif order.status == order.Cancelled:
        log_func(f"{direction} {order_type} ORDER CANCELLED.")

    elif order.status == order.Expired:
        log_func(f"{direction} {order_type} ORDER EXPIRED.")

    elif order.status == order.Rejected:  # notify_store() has the reason
        log_func(f"WARNING: {direction} {order_type} ORDER REJECTED!")

    elif order.status == order.Margin:
        log_func(f"WARNING: {direction} {order_type} ORDER MARGIN LIMIT!")
    else:
        log_func(f"WARNING: UNKNOWN ORDER STATUS: {order.status}")
