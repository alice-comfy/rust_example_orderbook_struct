import numpy as np
from time import perf_counter_ns
from numba import njit, int64, float64, bool_
from numba.experimental import jitclass
from scipy.stats import skewnorm
from numpy.typing import NDArray
#copied from : https://gist.github.com/beatzxbt/c6ea57983de849212837bc98ee8b2724

@njit(bool_[:](float64[:], float64[:]), nogil=True)
def isin(a: NDArray, b: NDArray) -> NDArray:
    out = np.empty(a.size, dtype=bool_)
    b = set(b)

    for i in range(a.size):
        out[i] = True if a[i] in b else False
            
    return out

spec = [
    ('size', int64),
    ('asks', float64[:, :]),
    ('bids', float64[:, :]),
    ('bba', float64[:, :])
]

@jitclass(spec)
class Orderbook:
    def __init__(self, size: int) -> None:
        self.size = size
        self.asks = np.empty((self.size, 2), dtype=float64)
        self.bids = np.empty((self.size, 2), dtype=float64)
        self.bba = np.empty((2, 2), dtype=float64)

    def _sort_book_(self) -> None:
        self.asks = self.asks[self.asks[:, 0].argsort()][:self.size]
        self.bids = self.bids[self.bids[:, 0].argsort()][::-1][:self.size]
        self.bba[0, :] = self.bids[0]
        self.bba[1, :] = self.asks[0]

    def _process_book_(self, book: NDArray, update: NDArray) -> NDArray:
        book = book[~isin(book[:, 0], update[:, 0])]
        return np.vstack((book, update[update[:, 1] != 0]))

    def initialize(self, asks: NDArray, bids: NDArray) -> None:
        self.asks[:, :] = asks
        self.bids[:, :] = bids
        self._sort_book_()

    def update_book(self, asks: NDArray, bids: NDArray) -> None:
        self.asks = self._process_book_(self.asks, asks)
        self.bids = self._process_book_(self.bids, bids)
        self._sort_book_()
        
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
    orderbook = Orderbook(levels)

    # Initialize book
    bids, asks = generate_near_mid_ob_levels(levels, mid_price=mid_price)
    orderbook.initialize(asks, bids)

    times_ns = []

    for _ in range(iters):
        bids, asks = generate_near_mid_ob_levels(int(levels**0.5), mid_price=mid_price)
        t1 = perf_counter_ns()
        orderbook.update_book(asks, bids)
        t2 = perf_counter_ns()
        times_ns.append(t2-t1)
        mid_price += (np.random.random() - 0.5) / 10
    
    mean = np.mean(times_ns)//1_000
    p50 = np.percentile(times_ns, 50)//1_000
    p95 = np.percentile(times_ns, 95)//1_000
    p99 = np.percentile(times_ns, 99)//1_000
    
    print(f"Mean: {mean}us | p50: {p50}us | p95: {p95}us | p99: {p99}us ")

    return None
    
orderbook_performance_testing(25, iters=10000)