//This code is intended for education / example purposes only. 
//(C) shinoji research 2023

use std::{cmp::Eq, collections::{btree_map, BTreeMap}};
use chrono::{DateTime, Utc, TimeZone};
//the basic idea here is that we convert the price / size to and integer and retain a multiplier to convert it back. The reasoning is to avoid the imprecision of floating point math. 
#[derive(Debug, Clone)]
pub struct OrderBook {
    symbol: String,
    pricePrecision: u8, 
    sizePrecision: u8,
    bids: BTreeMap<i64, i64>,
    asks: BTreeMap<i64, i64>
    
    
}
impl OrderBook {
    pub fn update_record(&mut self, new: OrderBookEntry) {
        let side = new.side.clone();
        let (price, size) = new.to_map();
        match side {
            Side::Buy => {
                if size > 0 {
                self.bids.insert(price, size);
                } else {
                    self.bids.remove(&price);
                }

            },
            Side::Sell => {
                if size > 0 {
                self.asks.insert(price, size);
                }
                else {
                    self.asks.remove(&price);
                }
            
            },
            
        }

    }
    pub fn new(symbol: String, pricePrecision: u8, sizePrecision: u8) -> Self {
        OrderBook { symbol: symbol, pricePrecision: pricePrecision, sizePrecision: sizePrecision, bids: BTreeMap::new(), asks: BTreeMap::new() }

    }
    pub fn get_best_BA(&self) -> (String, String) {
        let b = self.bids.clone();
        let a = self.asks.clone();
        let best_ask = self.to_string_price(a.keys().next().unwrap_or(&0).to_owned());
        let best_bid = self.to_string_price(b.keys().rev().next().unwrap_or(&0).to_owned());
        (best_bid, best_ask)
        
    }
    pub fn get_symbol(&self) -> &str {
        &self.symbol
    }
    pub fn check_order_profitabilty(&self, price: String, size: String, side: Side) {


    }
    pub fn get_slippage(&self, sz: String) -> String {
        let size = self.handle_string_size(sz);
        let b = self.bids.clone();
        let a = self.asks.clone();
        let best_ask = a.keys();
        let best_bid = b.keys().rev();
        let mut bsize = 0;
        let mut asize = 0;
        let mut bprice: i64= 1;
        let mut aprice: i64= 1 ;
        for bid in best_bid {
            bsize += b.get(bid).unwrap(); 
            if bsize > size {
                bprice = bid.to_owned();
                break;
            }
        }
        for ask in best_ask {
            asize += a.get(ask).unwrap(); 
            if bsize > size {
                aprice = ask.to_owned();
                break;
            }
        }
        self.to_string_price(aprice-bprice)
    }
    pub fn get_midprice_size(&self, sz: String) -> String {
        let size = self.handle_string_size(sz);
        let b = self.bids.clone();
        let a = self.asks.clone();
        let best_ask = a.keys();
        let best_bid = b.keys().rev();
        let mut bsize = 0;
        let mut asize = 0;
        let mut bprice: i64= 1;
        let mut aprice: i64= 1 ;
        for bid in best_bid {
            bsize += b.get(bid).unwrap(); 
            if bsize > size {
                bprice = bid.to_owned();
                break;
            }
        }
        for ask in best_ask {
            asize += a.get(ask).unwrap(); 
            if bsize > size {
                aprice = ask.to_owned();
                break;
            }
        }
        self.to_string_price(aprice-(aprice-bprice)/2)
    }
    pub fn get_spread(&self, book2: Self,  sz: String) -> String { //get the premium (discount) of one book against another. 
        let selfmid = self.handle_string_price(self.get_midprice_size(sz.clone()));
        let book2mid = book2.handle_string_price(book2.get_midprice_size(sz));
        let spread = selfmid - book2mid;
        self.to_string_price(spread)

    }
    //handle string / price functions are helper functions to translate too & from human / exchange readable and computer integer. 
    fn handle_string_price(&self, price: String ) -> i64 {
        let tmpprice :f64 = price.parse().unwrap();
        let expbase : i64 = 10;
        let finprice : i64 = (tmpprice* ((expbase.pow(self.pricePrecision as u32))as f64)) as i64;
        finprice
    }
    fn to_string_price(&self, price: i64) -> String {
        let expbase : i64 = 10;
        let res = ((price as f64)/(expbase.pow(self.pricePrecision as u32) ) as f64).to_string();
        res

    }
    fn handle_string_size(&self, size: String ) -> i64 {
        let tmpprice :f64 = size.parse().unwrap();
        let expbase : i64 = 10;
        let finprice : i64 = (tmpprice* ((expbase.pow(self.sizePrecision as u32))as f64)) as i64;
        finprice
    }
    fn to_string_size(&self, size: i64) -> String {
        let expbase : i64 = 10;
        let res = ((size as f64)/(expbase.pow(self.sizePrecision as u32) ) as f64).to_string();
        res

    }
}
