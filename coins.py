#!/usr/bin/env python
import urllib, json, os, sys
import ConfigParser
from influxdb import InfluxDBClient

config = ConfigParser.ConfigParser()
config.read(os.path.dirname(sys.argv[0]) + '/config.ini')

influx = InfluxDBClient(config.get('influx', 'host'),
                        config.get('influx', 'port'),
                        config.get('influx', 'user'),
                        config.get('influx', 'password'),
                        config.get('influx', 'db'),
                        )

def weiToEth(wei):
  return wei / 1000000000000000000;

def get_wallet(currency, address):
    try:
        url = "https://api.blockcypher.com/v1/" + currency + "/main/addrs/" + \
                address + "/balance"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        return float(data['final_balance'])
    except Exception, e:
        print "Ah oh something shit the bed. Continuing Anyway"
        print e
        pass

def get_currency_values():
    try:
        url = "https://poloniex.com/public?command=returnTicker";
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        return data
    except Exception, e:
        print "Ah oh something shit the bed. Continuing Anyway"
        print e
        pass


def put_wallet_influx(influx, currency, address, value, usd, btc):
    try:
        json_body = [
            {
                "measurement" : "coins",
                "tags": {
                    "currency": currency,
                    "address": address,
                },
                "fields": {
                    "value": float(value),
                    "usd": float(usd),
                    "btc": float(btc)
                }
            }
        ]
        influx.write_points(json_body)
    except Exception, e:
        print "Exception in Influx!"
        print e
        print "Continuing Anyway"
        pass

values = get_currency_values()

usdt_eth = float(values['USDT_ETH']['last'])
usdt_btc = float(values['USDT_ETH']['last'])
usdt_ltc = float(values['USDT_ETH']['last'])
btc_eth = float(values['BTC_LTC']['last'])
btc_ltc = float(values['BTC_LTC']['last'])

eth = weiToEth(get_wallet('eth', '0x44b4E6da63eA1e5C51715a138a17DaB612Cf329E'))
btc = get_wallet('btc', '1FPtv6RafvzX9yjkqR2hMTSEa1GPz621X5')
ltc = get_wallet('ltc', 'LMXdLUmr1Dt6hSbLqv1zbcku1BXtUEgifL')

put_wallet_influx(influx, 'eth', '0x44b4E6da63eA1e5C51715a138a17DaB612Cf329E', eth, usdt_eth * eth, btc_eth * eth)
put_wallet_influx(influx, 'btc', '1FPtv6RafvzX9yjkqR2hMTSEa1GPz621X5', btc, usdt_btc * btc, btc)
put_wallet_influx(influx, 'ltc', 'LMXdLUmr1Dt6hSbLqv1zbcku1BXtUEgifL', ltc, usdt_ltc * ltc, btc_ltc * ltc)
