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

    if len(trades) < mtg:
        with open("coin_list.txt") as f:
            for line in f:
                sell()
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

                    if up >= 5 and down >= -1.4 and red == False and down != 0 and i == 499:
                        for coin in trades:
                            if symbol.upper() == coin.upper():
                                posi = True
                        if posi == False:
                            print("buy")
                            buy(symbol=symbol, quantity=float(Quantity(symbol, mtg)))
                            trades.append(symbol.upper())
                            trades_price.append(current_price(symbol))
                            last_price.append(current_price(symbol) * -1)
                            save_trades()
                            with open("history.txt", "a") as f:
                                f.write(f"Buy - {symbol.upper()}: {'{:5.4f}'.format(current_price(symbol))}\n")

                    if red == False:
                        down = 0
                    elif red and up < 5:
                        up = 0
                    i += 1

def sell():
    global trades, trades_price, last_price

    i = len(trades) - 1
    while i >= 0:
        price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
        price = float(price['price'])

        if float(price) > float(last_price[i]):
            last_price[i] = price

        if float(price) < (float(trades_price[i]) * 0.99) or float(price) < (float(last_price[i]) * 0.995):
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








"""
symbol = ""
bricks = ""
last_message = ""
last_date = ""
sar = 0
run = True
mtg = 5

trades = []
trades_price = []
trades_price2 = []
banned_coins = []

client = Client(api_key="", api_secret="")



def ema_func():
    global bricks
    ema = 0
    for i in range(len(bricks) - 399, len(bricks) - 199):
        ema = float(bricks[i][4]) + ema
    ema = ema / 200

    for i in range(len(bricks) - 199, len(bricks)):
        ema = (float(bricks[i][4]) * (2 / 201)) + (ema * (1 - (2 / 201)))
    print(ema)
    if float(bricks[len(bricks) - 1][4]) > ema:
        return True
    else:
        return False

def macd_func():
    global bricks
    ema_fast = 0
    ema_slow = 0
    for i in range(len(bricks) - 23, len(bricks) - 11):
        ema_fast = float(bricks[i][4]) + ema_fast
    ema_fast = ema_fast / 12

    for i in range(len(bricks) - 51, len(bricks) - 25):
        ema_slow = float(bricks[i][4]) + ema_slow
    ema_slow = ema_slow / 26

    for i in range(len(bricks) - 11, len(bricks)):
        ema_fast = (float(bricks[i][4]) * (2 / 13)) + (ema_fast * (1 - (2 / 13)))

    for i in range(len(bricks) - 25, len(bricks)):
        ema_slow = (float(bricks[i][4]) * (2 / 27)) + (ema_slow * (1 - (2 / 27)))

    if ema_fast - ema_fast/200 > ema_slow:
        return True
    else:
        return False

def sar_func():
    global bricks, sar
    sar_bool = False
    lowest = 0
    highest = 0
    counter = 1

    for i in range(len(bricks) - 200, len(bricks)):
        price_highest = float(bricks[i][2])
        price_lowest = float(bricks[i][3])

        if price_highest > highest and sar_bool:
            highest = price_highest
            if counter < 10:
                counter += 1

        if price_lowest < lowest and sar_bool == False:
            lowest = price_lowest
            if counter < 10:
                counter += 1

        if sar_bool == False and sar < price_highest:
            sar_bool = True
            counter = 1
            sar = lowest
            highest = lowest
        elif sar_bool and sar > price_lowest:
            sar_bool = False
            counter = 1
            sar = highest
            lowest = highest

        if sar_bool:
            sar = sar + (0.02 * counter) * (highest - sar)
        else:
            sar = sar + (0.02 * counter) * (lowest - sar)

    return sar_bool

def linear_regression():
    global bricks

    length = 10

    x = numpy.array([])
    for i in range(0, length):
        x = numpy.append(x, i)

    y = numpy.array([])
    for i in range(len(bricks) - 1 - length, len(bricks) - 1):
        y = numpy.append(y, float(bricks[i][3]))

    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y * x) - n * m_y * m_x
    SS_xx = np.sum(x * x) - n * m_x * m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx

    if b_1 > 0:
        return True
    else:
        return False

def remove_line(fileName, lineToSkip): #Removes a given line from a file
    with open(fileName, 'r') as read_file:
        lines = read_file.readlines()

    currentLine = 1
    with open(fileName, 'w') as write_file:
        for line in lines:
            if currentLine == lineToSkip:
                pass
            else:
                write_file.write(line)
            currentLine += 1

def telegram():
    global last_message, last_date, mtg, run
    message = check_for_message().lower()
    date = check_for_message_date()

    if date != last_date:
        print(message)

        if message == "/end":
            send_message("Beendet")
            last_message = ""

        elif message == "stop" or message == "/stop":
            print("stop")
            if run:
                send_message("stopped")
            else:
                send_message("already stopped")
            run = False
            last_message = message
        elif message == "start" or message == "/start":
            if run:
                send_message("already started")
            else:
                send_message("started")
            print("start")
            run = True
            last_message = message

        elif message == "help" or message == "/help":
            print("help")
            send_message("Start - /start\nStop - /stop\nMoney - /wallet\nHistory - /history\nSettings - /settings")

        elif message == "/settings" or message == "settings":
            with open("bought_coins.txt", "r") as f:
                send_message(f.read())

        elif message == "/wallet" or message == "wallet":
            with open("USDT.txt", "r") as f:
                geld = float(f.read())
            current_value = 0
            i = len(trades) - 1
            while i >= 0:
                price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
                price = float(price['price'])
                print(price)
                with open("coins/" + trades[i].upper() + ".txt", 'r') as f:
                    current_value = current_value + (float(f.read()) * price)
                i -= 1
            send_message(f"USD: {str(geld)}\nCoins: \nCurrent Value: {str(current_value + geld)}")
            last_message = ""

        elif message == "/history" or message == "history":
            f = open("history.txt", "r")
            send_message(str(f.read()))
            f.close()

        elif message == "//kill":
            send_message("Good buy Motherfucker <3")
            last_message = message
            sys.exit(0)
        last_date = date

def coin_sell():
    global trades, trades_price, trades_price2, banned_coins

    print("sell")
    i = len(trades) - 1
    while i >= 0:
        price = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=' + trades[i].upper()).json()
        price = float(price['price'])
        print(trades[i], price)
        if float(price) < float(trades_price[i]) or float(price) > float(trades_price2[i]):
            sell_all(trades[i])
            print(2)
            with open("history.txt", "a") as f:
                f.write("Sell - " + trades[i] + "  " + '{:5.4f}'.format(price) + "\n")

            banned_coins.append(symbol.upper())
            print(1)
            print(trades[i], "Sold")
            trades.pop(i)
            trades_price.pop(i)
            trades_price2.pop(i)
            print(3)

            save_trades()
            i = len(trades)
        i -= 1

def coin_buy():
    global trades, trades_price, trades_price2, banned_coins, bricks, mtg

    print("buy")
    if len(trades) < mtg:
        with open("coin_list.txt") as f:
            for line in f:
                symbol = line.strip()
                contains = True
                reason = False
                bricks = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m').json()  # Todo: Timeframe Limit

                if len(trades) < mtg and linear_regression() and sar_func() and macd_func():
                    for coin in banned_coins:
                        if coin.upper() == symbol.upper():
                            reason = True

                    if reason == False:
                        contains = False
                        for i in trades:
                            if i.upper() == symbol.upper():
                                contains = True
                else:
                    for coin in banned_coins:
                        if coin.upper() == symbol.upper():
                            banned_coins.remove(symbol.upper())

                if contains == False:
                    if sar == 0:
                        banned_coins.append(symbol.upper())
                    else:
                        trades.append(symbol.upper())
                        print(trades)
                        trades_price.append(sar)
                        trades_price2.append((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4]))
                        buy(symbol, Quantity(symbol, mtg))
                        f = open("history.txt", "a")
                        f.write("Buy - " + symbol + "  " + '{:5.4f}'.format(bricks[len(bricks) - 1][4]) + " - " + '{:5.4f}'.format(sar) + " - " + '{:5.4f}'.format((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])) + "\n")
                        f.close()
                        print(symbol, "bought, Sellprice = ", str(sar), str((float(bricks[len(bricks) - 1][4]) - sar) + float(bricks[len(bricks) - 1][4])))
                        save_trades()

if __name__ == '__main__':

    with open("history.txt", "a") as f:
        f.write(str(time.time()) + "\n")
        print("writen by Handschuh Christoph and Timo Perzi <3")

    with open("coin_list.txt", "r+") as f:
        zeile = 0
        for line in f:
            symbol = line.strip().lower()
            zeile += 1
            with open("coins/" + symbol.upper() + ".txt", "w") as d:
                d.write(str(0))
            try:
                brick = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + '&interval=30m')  # Todo: Timeframe Limit
                bricks = brick.json()
            except requests.exceptions.RequestException as e:
                print("Error: /n ", e)

            if "Invalid symbol" in brick.text:
                print("removed invalid symbol: ", symbol.upper())
                remove_line("coin_list.txt", zeile)

            elif macd_func() and linear_regression() and sar_func():
                banned_coins.append(symbol.upper())
    print(f"banned_coins: {banned_coins}")

    restore_last_trades()

    while True:
        start = time.time()

        telegram()

        if run:
            if mtg == len(trades):
                with open("coin_list.txt", "r+") as f:
                    x = 0
                    for line in f:
                        symbol = line.strip().lower()

                        if macd_func() and linear_regression() and sar_func():
                            banned_coins.append(symbol.upper())
                print(f"banned_coins: {banned_coins}")
            else:
                coin_buy()
            coin_sell()

        ende = time.time()
        print('{:5.3f}s'.format(ende - start))
"""