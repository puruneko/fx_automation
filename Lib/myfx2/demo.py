import queue
import threading
import time

from order import Order
from trade import Trade
from settings import STREAM_DOMAIN, API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID
from strategy import Strategy
from streaming import StreamingForexPrices

if __name__ == "__main__":
    heartbeat = 3  # 5 second between polling
    events = queue.Queue()

    # Trade 10000 units of EUR/USD
    instrument = "EUR_USD"
    units = 10000

    # heartbeat

    # Create the OANDA market price streaming class
    # making sure to provide authentication commands
    prices = StreamingForexPrices(
        ACCESS_TOKEN, ACCOUNT_ID,
        instrument, events
    )

    # Create the execution handler making sure to
    # provide authentication commands
    order = Order(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID)

    # Create the strategy/signal generator, passing the
    # instrument, quantity of units and the events queue
    strategy = Strategy(instrument, units, events)

    trade = Trade(events, strategy, order, heartbeat)

    with open("history_event.txt", "w") as file:
        file.write("start\n")

    # Create two separate threads: One for the trading loop
    # and another for the market price streaming class
    trade_thread = threading.Thread(target=trade.start, args=[])
    price_thread = threading.Thread(target=prices.stream_to_queue, args=[])

    # Start both threads
    trade_thread.start()
    price_thread.start()
