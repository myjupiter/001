import os
import sys
import time
import json
import requests
import urllib
from multiprocessing import Process
#from termcolor import colored
import logging
from common import blockDraw
from utils import getLength, redigit, tstodate, getSignature, getHeaders, busdTotal, green, red
from useragent import Agent
from screen import drawLine, clearLine
from ws import MarketUpdate

usleep = lambda x: time.sleep(x/1000000.0)

def exchangeInfo(q):
    logging.info("exchangeInfo")
    store = q.get()
    apiKey = store['api']['key']
    apiSecret = store['api']['secret']
    endPoint = store['api']['endpoint']
    path = store['api']['infoPath']
    if True:
    #try:
        limit = 5
        apiPath = "{0}".format(path)
        url="{0}/{1}".format(endPoint, apiPath)
        headers = {'User-Agent': Agent('brave')}
        getResp = requests.get(url, headers=headers)
        if getResp.status_code == 200:
            r = json.loads(getResp.content)
            store['symbols'] = r['symbols']
            #length = len(r['symbols'])
            #logging.info(length)
            #logging.info(json.dumps(r, indent=3))
            #return True
        elif getResp.status_code == 400:
            logging.info(getResp)
        else:
            logging.info(getResp)
            logging.info("coinPrice get error")
    #except:
    #    logging.info("coinsList error")
    #    pass

    q.put(store)


def binanceWallet(q):
    store = q.get()
    if store is not None:
        apiKey = store['api']['key']
        apiSecret = store['api']['secret']
        endPoint = store['api']['endpoint']
        path = store['api']['accountPath']
        timeStamp = int(time.time()*1000)
        queryObj = {
                "recvWindow": 5000,
                "timestamp": timeStamp
                }
        queryString = urllib.parse.urlencode(queryObj, doseq=False)
        signature = getSignature(apiSecret, queryString)
        if signature is not None:
            apiPath = "{0}?{1}".format(path, queryString)
            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
            headers = getHeaders(apiKey)
            try:
                response=requests.get(url, headers=headers)
                if response.status_code == 200:
                    r=json.loads(response.content)
                    exchange = store['exchange']
                    #logging.info(json.dumps(r, indent=3))
                    exchangeText = green(exchange.upper())
                    if r['canTrade']:
                        store['canTrade'] = True
                    else:
                        exchangeText = red(exchange.upper())

                    hAsset = store['hAsset']
                    start = hAsset
                    reverse = False
                    nextColumn = 0
                    space = 3
                    maxLength = 0
                    lst = ['asset', 'free', 'locked']
                    lines = {}
                    for v in lst:
                        lines[v] = start
                        start += 1

                    exist = False

                    total = busdTotal(r['balances'], store, q)
                    #total = "BUSD: 10"
                    logging.info(total)
                    store['busd'] = total

                    coinsWallet = []
                    for i,v in enumerate(r['balances']):
                        asset = v['asset']
                        if asset not in store['coinsWallet']:
                            coinsWallet.append(asset)
                        free = float(v['free'])
                        locked = float(v['locked'])
                        if not exist:
                            exist = True
                            text = "%s %s" % (exchangeText, total)
                            line = hAsset - 1
                            obj = json.dumps({
                                    "text": text,
                                    "line": line,
                                    "column": 0,
                                    "length": len(text),
                                    "reverse": reverse
                                    })
                            drawLine(obj, True)

                            obj = {
                                    "lines": lines,
                                    "nextColumn": nextColumn,
                                    "space": space,
                                    "lst": lst,
                                    "reverse": reverse
                                    }
                            nextColumn = blockDraw(json.dumps(obj), True)

                        if free > 0.00 or locked > 0.00:
                            lst = [asset, free, locked]
                            obj = {
                                    "lines": lines,
                                    "nextColumn": nextColumn,
                                    "space": space,
                                    "lst": lst,
                                    "reverse": reverse
                                    }
                            nextColumn = blockDraw(json.dumps(obj), True)

                    store['endWallet'] = start + space
                    store['coinsWallet'] = coinsWallet
                    q.put(store)
            except:
                pass

def wsCall(sym, q):
    x = MarketUpdate(sym, q)
    x.run()
    time.sleep(0.1)

def binanceBids(limit, q):
    logging.info("recall bids, asks")
    store = q.get()
    if store is not None:
        #logging.info(store['actionCoins'])
        #apiKey = store['api']['key']
        #apiSecret = store['api']['secret']
        #endPoint = store['api']['endpoint']
        #path = store['api']['bidPath']
        #logging.info(store['actionCoins'])
        if len(store['actionCoins']) > 0:
            pullings = store['pullings']
            log = "stores['pullings'] %s" % ( pullings )
            logging.info(pullings)
            for i,sym in enumerate(store['actionCoins']):
                if sym.lower() not in pullings:
                    log = "%s %s" % (i, sym.lower())
                    logging.info(log)

                    s = sym.lower()
                    wsCall(s, q)
                    #p = Process(target=wsCall, args=(s, q,))
                    #p.start()
                    #p.join()

                    pullings.append(sym.lower())
                    store['pullings'] = pullings
                    q.put(store)
                    time.sleep(1)
                    #if i > 0:
                    #    break
            #    #            queryObj = {
            #    #                "symbol": symbol,
            #                "limit": limit
            #            }
            #            queryString = urllib.parse.urlencode(queryObj, doseq=False)
            #            apiPath = "{0}?{1}".format(path, queryString)
            #            url="{0}/{1}".format(endPoint, apiPath)
            #            headers = {'User-Agent': Agent('brave')}
            #            getResp = requests.get(url, headers=headers)
            #            if getResp.status_code == 200:
            #                r = json.loads(getResp.content)
            #                # store asks and bids
            #                asks = "asks_%s" % (symbol.lower())
            #                store[asks] = r['asks']
            #                bids = "bids_%s" % (symbol.lower())
            #                store[bids] = r['bids']
            #                log = "bids: %s asks: %s %s: %s" % (len(r['bids']), len(r['asks']), i, symbol)
            #                logging.info(log)
            #                q.put(store)
            #            elif getResp.status_code == 400:
            #                logging.info("get last price error")
            #            else:
            #                logging.info("other error than 400")

            #            #time.sleep(0.01)
            #            usleep(1)
            #        #break
            #except:
            #    logging.info("there is error. be aware of exceed limit")
        log = " total pairs: %s" % len(store['symbols'])
        logging.info(log)

    q.put(store)

#def toggleTrade(q):
#    store = q.get()
#    if store is not None:
#        text = ""
#        if store['tradeSell'] or store['tradeBuy']:
#            bid = green(store['tradeBuy'])
#            ask = green(store['tradeSell'])
#            if store['tradeBuy']:
#                bid = red(store['tradeBuy'])
#            if store['tradeSell']:
#                ask = red(store['tradeSell'])
#
#            text = "Bid: %s Ask: %s" % (bid, ask)
#        else:
#            text = "Trade: Stopped"
#            text = colored(text, 'green')
#
#        obj = json.dumps({
#                "text": text,
#                "line": 4,
#                "column": 30,
#                "length": 20,
#                #"length": len(text),
#                "reverse": True
#                })
#
#        #clearRow(obj)
#        drawLine(obj)

#def marketTicker(q):
#    store = q.get()
#    if store is not None:
#        apiKey = store['key']
#        secretKey = store['secret']
#        endPoint = store['endpoint']
#        timeStamp = int(time.time()*1000)
#        queryObj = {
#                "symbol": "BNBBTC",
#                }
#        queryString = urllib.parse.urlencode(queryObj, doseq=False)
#        apiPath = "ticker/24hr?{0}".format(queryString)
#        url="{0}/{1}".format(endPoint, apiPath)
#        headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
#        response=requests.get(url, headers=headers)
#        if response.status_code == 200:
#            r=json.loads(response.content)
#            #logging.info(r)
#
#def reloadHistory(q, limit):
#    store = q.get()
#    if store is not None:
#        apiKey = store['key']
#        secretKey = store['secret']
#        endPoint = store['endpoint']
#        for _, coin in enumerate(store['executeCoins']):
#            timeStamp = int(time.time()*1000)
#            queryObj = {
#                    "symbol": "{}BUSD".format(coin),
#                    "timestamp": timeStamp,
#                    "limit": limit
#                    }
#            queryString = urllib.parse.urlencode(queryObj, doseq=False)
#            signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
#            apiPath = "allOrders?{0}".format(queryString)
#            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
#            headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
#            #logging.info(url)
#            #logging.info(headers)
#            response=requests.get(url, headers=headers)
#            #logging.info(response.status_code)
#            if response.status_code == 200:
#                r=json.loads(response.content)
#                #logging.info(json.dumps(r, indent=3))
#                columns = ['time', 'symbol', 'side', 'price', 'origQty', 'executedQty']
#                #size = os.get_terminal_size()
#                #startLine =  int(size.lines / 4)
#                startLine = 11
#                startColumn = 0
#                reverse = False
#                lst = sorted(r, key=lambda k: k['time'], reverse=True)
#                for k,v in enumerate(lst):
#                    if v['status'] == "FILLED":
#                    #if v['status'] == "CANCELED":
#                        texts = []
#                        for a,b in enumerate(columns):
#                            value = v[b]
#                            if b == "time":
#                                value = tstodate(v[b])
#
#                            if b == "price":
#                                value = redigit(v[b], 2, True)
#
#                            if b == "origQty":
#                                value = redigit(v[b], 5, True)
#
#                            if b == "executedQty":
#                                value = redigit(v[b], 5, True)
#
#                            if b == "side":
#                                if v[b] == "BUY":
#                                    value = colored("BUY ", "green")
#
#                            if b == "side":
#                                if v[b] == "SELL":
#                                    value = colored(v[b], "red")
#
#                            texts.append(str(value))
#
#                        display = " ".join(texts)
#                        obj = json.dumps({
#                                "text": display,
#                                "line": startLine,
#                                "column": startColumn,
#                                "length": 0,
#                                "reverse": reverse
#                                })
#
#                        drawLine(obj)
#                        startLine += 1

#def reloadOrderStatus(q):
#    store = q.get()
#    if store is not None:
#        apiKey = store['key']
#        secretKey = store['secret']
#        endPoint = store['endpoint']
#        for _, coin in enumerate(store['executeCoins']):
#            timeStamp = int(time.time()*1000)
#            queryObj = {
#                    "symbol": "{}BUSD".format(coin),
#                    "timestamp": timeStamp
#                    }
#            queryString = urllib.parse.urlencode(queryObj, doseq=False)
#            signature = hmac.new(bytes(secretKey, 'latin-1'), msg=bytes(queryString, 'latin-1'), digestmod=hashlib.sha256).hexdigest()
#            apiPath = "openOrders?{0}".format(queryString)
#            url="{0}/{1}&signature={2}".format(endPoint, apiPath, signature)
#            headers = {'User-Agent': Agent('brave'), 'X-MBX-apiKey': apiKey}
#            response=requests.get(url, headers=headers)
#            if response.status_code == 200:
#                r=json.loads(response.content)
#                #logging.info(json.dumps(r, indent=3))
#                lines = {}
#                startLine = 14
#                side = "BUY"
#                for i, v in enumerate(r):
#                    if v['side'] == "SELL":
#                        side = "SELL"
#                        startLine += 6
#
#                lines['pair'] = startLine
#                startLine += 1
#                lines['amt'] = startLine
#                startLine += 1
#                lines['filled'] = startLine
#                startLine += 1
#                lines['time'] = startLine
#                reverse = True
#                if len(r) > 0:
#                    space = 3
#                    maxLength = 0
#                    nextColumn = 0
#                    for x in lines:
#                        constant = 100
#                        #clearLine(lines[x], constant,  reverse)
#                        #clearLine(lines[x], store['endedBuy'], reverse)
#
#                    valuee = []
#                    for i, v in enumerate(r):
#                        pair = v['symbol']
#                        total = float(v['origQty']) * float(v['price'])
#                        amt = "{0} @ {1}".format(redigit(total, 2, True), redigit(v['price'], 2, True))
#                        filled = (float(v['executedQty'])/100) * float(v['origQty'])
#
#                        t = []
#                        for x in lines:
#                            t.append(x)
#
#                        texts = {}
#                        texts[t[0]] = pair
#                        texts[t[1]] = amt
#                        texts[t[2]] = "{}%".format(redigit(filled, 2))
#                        texts[t[3]] = tstodate(v['time'])
#
#                        array = []
#                        for x in lines:
#                            array.append(texts[x])
#
#                        maxLength = getLength(array)
#                        for x in lines:
#                            obj = json.dumps({
#                                "text": texts[x],
#                                "line": lines[x],
#                                "column": nextColumn,
#                                "length": maxLength,
#                                "reverse": reverse
#                                })
#
#                            drawLine(obj)
#                            #logging.info(obj)
#
#                        nextColumn = nextColumn + maxLength
#                        nextColumn += space
#                        store['endedBuy'] = nextColumn
#
#                else:
#                    for x in lines:
#                        #logging.info(lines[x])
#                        #logging.info(store['endedBuy'])
#                        constant = 100 # constant fix it later
#                        #clearLine(lines[x], constant, reverse)

#def showAsset(b, j):
#    c = json.loads(b)
#    space = 3
#    line = 10
#    asset = c['asset']; free = c['free']; locked = c['locked']
#
#    maxLength = getLength([asset, free, locked])
#    nextColumn = 0 + (maxLength * j)
#    if j > 0:
#        nextColumn = nextColumn + space
#        #if j > 1:
#        #    nextColumn += 1 # bug fix it
#
#    for x in c:
#        text = c[x]
#        try:
#            if x == "locked":
#                if float(c[x]) > 0.00:
#                    text = colored(c[x], 'red')
#        except:
#            pass
#
#        obj = json.dumps({
#            "text": text,
#            "line": line,
#            "column": nextColumn,
#            "length": maxLength,
#            "reverse": True
#            })
#        drawLine(obj)
#        line += 1
#
#    #nextColumn = nextColumn + space
#
#def binanceWallet(q):
#    store = q.get()
#    if store is not None:
#        try:
#            j = 0
#            for i, b in enumerate(store['balanceCoins']):
#                if float(b['free']) > 0.0:
#                    showAsset(json.dumps(b), j)
#                    j += 1
#        except:
#            logging.info("Not found coins yet, please wait for next call")
#
