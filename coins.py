#!/usr/bin/env python
import urllib, json, os, sys
import ConfigParser
from influxdb import InfluxDBClient
from coinbase.wallet.client import Client

config = ConfigParser.ConfigParser()
config.read(os.path.dirname(sys.argv[0]) + '/config.ini')

coinbase_client = Client(config.get('coinbase', 'api_key'),
                         config.get('coinbase', 'api_secret'),
)

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

def get_coinbase_accounts(coinbase_client):
    coinbase_accounts = coinbase_client.get_accounts()
    account_dict = {}
    for account in coinbase_accounts.data:
      currency = account.currency
      balance = account.balance.amount
      #print currency
      #print balance
      account_dict[currency] = balance
    return account_dict

values = get_currency_values()

usdt_eth = float(values['USDT_ETH']['last'])
usdt_btc = float(values['USDT_BTC']['last'])
usdt_ltc = float(values['USDT_ETH']['last'])
usdt_bch = float(values['USDT_BCH']['last'])
btc_eth = float(values['BTC_LTC']['last'])
btc_ltc = float(values['BTC_LTC']['last'])
btc_bch = float(values['BTC_BCH']['last'])

# Coinbase
coinbase_accounts = get_coinbase_accounts(coinbase_client)
cb_eth = float(coinbase_accounts['ETH'])
cb_btc = float(coinbase_accounts['BTC'])
cb_bch = float(coinbase_accounts['BCH'])
cb_ltc  = float(coinbase_accounts['LTC'])
put_wallet_influx(influx, 'eth', 'Coinbase', cb_eth, usdt_eth * cb_eth, btc_eth * cb_eth)
put_wallet_influx(influx, 'btc', 'Coinbase', cb_btc, usdt_btc * cb_btc, cb_btc)
put_wallet_influx(influx, 'bch', 'Coinbase', cb_bch, usdt_bch * cb_bch, btc_bch * cb_bch)
put_wallet_influx(influx, 'ltc', 'Coinbase', cb_ltc, usdt_ltc * cb_ltc, btc_ltc * cb_ltc)

# Cold Storage Wallets
eth = weiToEth(get_wallet('eth', '0x44b4E6da63eA1e5C51715a138a17DaB612Cf329E'))
btc = get_wallet('btc', '1FPtv6RafvzX9yjkqR2hMTSEa1GPz621X5')
ltc = get_wallet('ltc', 'LMXdLUmr1Dt6hSbLqv1zbcku1BXtUEgifL')
put_wallet_influx(influx, 'eth', '0x44b4E6da63eA1e5C51715a138a17DaB612Cf329E', eth, usdt_eth * eth, btc_eth * eth)
put_wallet_influx(influx, 'btc', '1FPtv6RafvzX9yjkqR2hMTSEa1GPz621X5', btc, usdt_btc * btc, btc)
put_wallet_influx(influx, 'ltc', 'LMXdLUmr1Dt6hSbLqv1zbcku1BXtUEgifL', ltc, usdt_ltc * ltc, btc_ltc * ltc)
