import Orderbook_Struct
import numpy as np
from scipy.stats import skewnorm
from time import perf_counter_ns

##based on benchmark code written by "BeatzXBT" https://gist.github.com/beatzxbt/c6ea57983de849212837bc98ee8b2724

OB = Orderbook_Struct.OrderBook('BTCUSDT', 8,8) #SYMBOl doesn't matter but is required, 





def generate_near_mid_ob_levels(levels=25, zero_sizes=False, mid_price=100.0, spread=5.0, seed=0):
    # np.random.seed(seed)

    skewness = 5
    
    # Adjust loc and scale to control the mean and spread around the mid-price
    bids_prices = skewnorm.rvs(a=-skewness, loc=mid_price - spread / 2, scale=spread, size=levels)
    asks_prices = skewnorm.rvs(a=skewness, loc=mid_price + spread / 2, scale=spread, size=levels)
    
    sizes = np.round(np.random.rand(levels) * 10, 2)
    bids = np.vstack((np.round(bids_prices, 1), sizes)).T
    asks = np.vstack((np.round(asks_prices, 1), sizes)).T

    if zero_sizes:
        zero_qty_indices_bids = np.random.choice(range(levels), size=levels // 5, replace=False)
        zero_qty_indices_asks = np.random.choice(range(levels), size=levels // 5, replace=False)
        bids[zero_qty_indices_bids, 1] = 0
        asks[zero_qty_indices_asks, 1] = 0

    return bids, asks
    
def orderbook_performance_testing(levels=25, iters=100_000):
    mid_price = 100
    orderbook =  OB

    # Initialize book
    bids, asks = generate_near_mid_ob_levels(levels, mid_price=mid_price)
    asks = [(str(p), str(s)) for (p,s) in asks]
    bids = [(str(p), str(s)) for (p,s) in bids]
    orderbook.handle_new_bids_asks(bids, asks)

    times_ns = []

    for _ in range(iters):
        bids, asks = generate_near_mid_ob_levels(int(levels**0.5), mid_price=mid_price)
        asks = [(str(p), str(s)) for (p,s) in asks]
        bids = [(str(p), str(s)) for (p,s) in bids]
        t1 = perf_counter_ns()
        orderbook.handle_new_bids_asks(bids, asks)
        t2 = perf_counter_ns()
        times_ns.append(t2-t1)
        mid_price += (np.random.random() - 0.5) / 10
    
    mean = np.mean(times_ns)//1_000
    p50 = np.percentile(times_ns, 50)//1_000
    p95 = np.percentile(times_ns, 95)//1_000
    p99 = np.percentile(times_ns, 99)//1_000
    
    print(f"Mean: {mean}us | p50: {p50}us | p95: {p95}us | p99: {p99}us ")

    return None
    
orderbook_performance_testing(10000, iters=10000)