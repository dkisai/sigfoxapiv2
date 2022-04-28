# Sigfox API V2

Python wrapper around the Sigfox V2 API

## Install

`pip3 install git+ssh://git@github.com/barter4things/sigfoxapiv2.git`

## Usage

Simply create an instance of the Sigfox object and call the appropriate methods.

This uses `requests` internally, so the returned tuple (reponse code, reponse) as the same as using the requests library normally.

```python


```py
from sigfoxapiv2 import Sigfox
from pprint import pprint

sigfox = Sigfox("username", "password")

response_code, response = sigfox.create_device(
    id="FFFFFFFF",
    pac_code="FFFFFFFFFFFF",
    name="My Device",
    device_type_id="abc123",
    prototype=False,
    product_cert="P_Foobar_1",
)

pprint(response)
pprint(response)
```