import requests
import websocket
import sys
from ces import *
from multiprocessing import *
from binance.client import Client
from telegram import *
import time
print("writen by Handschuh Christoph and Timo Perzi <3")

mtg = 2

trades = []
trades_price = []
last_price = []

def restore_last_trades():
    global mtg, trades, trades_price, last_price

    with open("bought_coins.txt", "r+") as f:
        i = -1
        j = 0
        for line in f.readlines():
            line = line.strip()
            if i == -1:
                mtg = float(line)  # mtg
            elif i == 0:
                trades.append(line.lower())  # symbol
            elif i == 1:
                with open("coins/" + trades[j].upper() + ".txt", "w") as d:  # Coin holding
                    d.write(line)
                j += 1
            elif i == 2:
                trades_price.append(float(line))  # sell price -
                print(trades_price)
            elif i == 3:
                last_price.append(float(line))  # sell price +
                print(last_price)
            i += 1
            if i == 4:
                i = 0

def save_trades():
    global trades_price, last_price, trades, mtg

    with open("bought_coins.txt", "r+") as f:
        f.truncate()
        f.write(str(mtg) + "\n")  #mtg
        i = len(trades)-1
        while i >= 0:
            f.write(trades[i].upper() + "\n") #symbol
            with open("coins/" + trades[i].upper() + ".txt", "r+") as d: #Coin holding
                f.write(d.read() + "\n")
            f.write(str(trades_price[i]) + "\n")  #sell price +
            f.write(str(last_price[i]) + "\n")  # sell price -
            i -= 1

def buy_():
    global trades, trades_price, mtg, last_price

    a = 0
    if len(trades) < mtg:
        with open("coin_list.txt") as f:
            for line in f:
                if len(trades) != 0 and a == 15:
                    sell()
                    a = 0

                symbol = line.strip()
                bricks = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=1m').json()

                up = 0
                down = 0
                i = 480
                red = False
                posi = False

                while i != len(bricks):
                    diff = float(bricks[i][4]) - float(bricks[i][1])

                    if diff < 0:
                        down = down - ((float(bricks[i][4]) * 100) / float(bricks[i][1]) - 100)
                        red = True

                    elif diff >= 0:
                        up = up + ((float(bricks[i][4]) * 100) / float(bricks[i][1]) - 100)
                        red = False

                    if up >= 3.3 and down >= -1.11 and red == False and down != 0 and i == 499:
                        for coin in trades:
                            if symbol.upper() == coin.upper():
                                posi = True
                        if posi == False:
                            print("buy - " + coin.upper())
                            buy(symbol=symbol, quantity=float(Quantity(symbol, mtg)))
                            trades.append(symbol.upper())
                            trades_price.append(current_price(symbol))
                            last_price.append(current_price(symbol) * -1)
                            save_trades()
                            with open("history.txt", "a") as f:
                                f.write(f"Buy - {symbol.upper()}: {'{:5.4f}'.format(current_price(symbol))}\n")

                    if red == False:
                        down = 0
                    elif red and up < 3.3:
                        up = 0
                    i += 1
                a += 1

def sell():
    global trades, trades_price, last_price

    i = len(trades) - 1
    while i >= 0:
        price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
        price = float(price['price'])

        if float(price) > float(last_price[i]):
            last_price[i] = price

        if float(price) < (float(trades_price[i]) * 0.999) or float(price) < (float(last_price[i]) * 0.992):
            print("sell")
            sell_all(trades[i])
            save_trades()
            with open("history.txt", "a") as f:
                f.write("Sell - " + trades[i] + "  " + '{:5.4f}'.format(price) + "\n")

            trades.pop(i)
            trades_price.pop(i)
            last_price.pop(i)
            save_trades()
            i = len(trades)
        i -= 1

if __name__ == '__main__':

    with open("coin_list.txt", "r+") as f:
        for line in f:
            symbol = line.strip().lower()

            with open("coins/" + symbol.upper() + ".txt", "w") as d:
                d.write(str(0))

    restore_last_trades()

    while True:
        start = time.time()

        buy_()

        print('{:5.3f}s'.format(time.time() - start))
