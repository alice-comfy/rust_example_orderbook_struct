//for miscellaneous structs.
use std::fmt;

//in house decimal struct for simplicity. In production you probably want Rust Decimal crate.
#[derive(Debug, Clone, Copy)]
pub struct Decimal64 {
    //Stores decimal numbers as i64 
    underlying: i64,
    precision: u8,
    
}
impl PartialEq for Decimal64 {
    fn eq(&self, other: &Self) -> bool {
        self.underlying == other.underlying

    }
}
impl Decimal64{
    pub fn new(input: String, precision: u8) -> Self{
        let temp :f64 = input.parse().unwrap();
        let expbase: i64 = 10;
        let underlying = (temp * (expbase.pow(precision as u32 )) as f64) as i64;
        Self {
            underlying:underlying,
            precision: precision,
        }


    }
}
impl fmt::Display for Decimal64 {
    fn fmt(&self, f : &mut fmt::Formatter) -> fmt::Result {
        let pprint = (self.underlying as f64 / (10_i64.pow(self.precision as u32)) as f64);
        write!(f, "{}",pprint )
    }
}