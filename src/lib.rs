use pyo3::prelude::*;

mod orderbook;
mod models;
use crate::orderbook::OrderBook;

#[pymodule]
fn Orderbook_Struct(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<OrderBook>();
    Ok(())
}