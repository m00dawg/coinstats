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

def get_price(symbol):
    try:
        url = "https://poloniex.com/public?command=returnTicker";
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        return data[symbol]['last']
    except Exception, e:
        print "Ah oh something shit the bed. Continuing Anyway"
        print e
        pass


def put_wallet_influx(influx, currency, address, value, usd):
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
                    "usd": float(usd)
                }
            }
        ]
        influx.write_points(json_body)
    except Exception, e:
        print "Exception in Influx!"
        print e
        print "Continuing Anyway"
        pass


eth = weiToEth(get_wallet('eth', '0x44b4E6da63eA1e5C51715a138a17DaB612Cf329E'))
btc = get_wallet('btc', '1FPtv6RafvzX9yjkqR2hMTSEa1GPz621X5')
ltc = get_wallet('ltc', 'LMXdLUmr1Dt6hSbLqv1zbcku1BXtUEgifL')
put_wallet_influx(influx, 'eth', '0x44b4E6da63eA1e5C51715a138a17DaB612Cf329E', eth, get_price('USDT_ETH'))
put_wallet_influx(influx, 'btc', '1FPtv6RafvzX9yjkqR2hMTSEa1GPz621X5', btc, get_price('USDT_BTC'))
put_wallet_influx(influx, 'ltc', 'LMXdLUmr1Dt6hSbLqv1zbcku1BXtUEgifL', ltc, get_price("USDT_LTC"))
