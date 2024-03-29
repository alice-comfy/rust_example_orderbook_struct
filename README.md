Example pulled from monorepo of how you might store an orderbook data structure in rust. Includes functions to calculate the midprice from this data. In this update I've added a pyo3 connector so that this module can be used within Python.

Personally I would recommend writing your connector & orderbook module in Rust and connecting to Python via gRPC or Websockets. The GIL has no place in live / real time applications.

See: https://github.com/alice-comfy/SeismicDB for permanent data storage.

All code (C) myself
