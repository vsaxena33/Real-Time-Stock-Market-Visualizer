"""
================================================================================
REAL-TIME STOCK MARKET VISUALIZER
================================================================================
This program connects to the Fyers Stock Exchange API to create a live-updating 
"Candlestick Chart" for Reliance Industries (RELIANCE-EQ).

Think of this as an automated digital artist:
1. It looks at what happened in the market earlier today (Historical Data).
2. It waits for the "heartbeat" of the market (Live Ticks).
3. Every time a new price comes in, it updates the drawing in real-time.

Author: Vaibhav Saxena
================================================================================
"""

# ============================================================
# Imports
# ============================================================
from fyers_apiv3.FyersWebsocket import data_ws
import pandas as pd
import pytz
import datetime as dt
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from fyers_apiv3 import fyersModel
from credentials import client_id

# ============================================================
# SETTINGS / CONFIGURATION
# ============================================================
SYMBOL = 'NSE:RELIANCE-EQ'
TIMEZONE = 'Asia/Kolkata'
MAX_CANDLES = 100
PLOT_WINDOW = 10

# ============================================================
# Update Logic for Live Data
# ============================================================
def update_live_data(data, message, last_total_volume) -> tuple[pd.DataFrame, int]:
    """
    Update the OHLCV dataframe using incoming websocket tick data.

    The websocket provides cumulative traded volume for the session.
    This function converts cumulative volume into incremental candle volume.

    Parameters
    ----------
    data : pandas.DataFrame
        Existing OHLCV dataframe indexed by timestamp.

    message : dict
        Incoming websocket tick message from Fyers.

    last_total_volume : int or None
        Previous cumulative traded volume received from websocket.

    Returns
    -------
    tuple
        Updated dataframe and latest cumulative traded volume.
    """

    # If the message is empty or broken, don't do anything
    if "symbol" not in message:
        return data, last_total_volume
    
    ltp = message.get('ltp')                            # LTP = Last Traded Price (The current market price)

    if ltp is None:
        return data, last_total_volume
    
    # Cumulative volume is the total shares traded since 9:15 AM. 
    # We want to find out how many were traded just in the last tick.
    total_vol = message.get('vol_traded_today')
    
    # Create a timestamp rounded to the current minute (e.g., 10:05:42 becomes 10:05:00)
    timestamp = pd.Timestamp.now(tz=TIMEZONE).floor('1min')

    if total_vol is None:
        total_vol = last_total_volume if last_total_volume is not None else 0

    # Logic to calculate 'Incremental Volume' (New Volume = Current Total - Previous Total)
    if last_total_volume is None:
        incremental_vol = 0
    else:
        incremental_vol = total_vol - last_total_volume

    if incremental_vol < 0:
        incremental_vol = 0

    if len(data) > 0 and data.index[-1] == timestamp:
        # If we are still in the same minute, we update the existing candle
        data.iloc[-1, 3] = ltp                          # Close price continuously tracks latest traded price
        data.iloc[-1, 1] = max(data.iloc[-1, 1], ltp)   # Update High if price went higher
        data.iloc[-1, 2] = min(data.iloc[-1, 2], ltp)   # Update Low if price went lower
        data.iloc[-1, 4] += incremental_vol             # Add the new volume to the minute's total
    else:
        # If a new minute has started, create a brand new candle (row) in our table
        new_candle = pd.DataFrame(
            [{
                'open': ltp,
                'high': ltp,
                'low': ltp,
                'close': ltp,
                'volume': incremental_vol
            }],
            index=[timestamp]
        )
        data = data.tail(MAX_CANDLES)                   # Keep only the last MAX_CANDLES candles to limit memory usage
        data = pd.concat([data, new_candle])

    return data, total_vol

# ============================================================
# Historical Data Fetching
# ============================================================
def fetch_historical_data(fyers: fyersModel.FyersModel) -> pd.DataFrame:
    """
    Before starting the live chart, we need to know what happened earlier 
    in the day so the chart doesn't start from a blank screen.
    """
    
    now = dt.datetime.now(pytz.timezone('Asia/Kolkata'))

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    previous_time = start_of_day.timestamp()
    current_time = now.timestamp()

    nifty_data = {
        "symbol": SYMBOL,
        "resolution": "1",  # "1" means 1-minute intervals
        "date_format": "0",
        "range_from": int(previous_time),
        "range_to": int(current_time),
        "cont_flag": "1"
    }

    # Ask Fyers for the data and convert it into an Excel-like table (DataFrame)
    response = fyers.history(data=nifty_data)
    historical_data = response['candles']
    df = pd.DataFrame(historical_data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    
    # Fix the time format so humans and computers can read it easily
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert(pytz.timezone('Asia/Kolkata'))
    df.set_index('date', inplace=True)
    return df

# ============================================================
# Plotting the Candlestick Chart
# ============================================================
def plot_chart(candlestick):
    """
    This function handles the 'UI' (User Interface). 
    It creates the window and draws the candles.
    """
    # Create a figure with two parts: Ax (Price chart) and Ax_vol (Volume bars at bottom)
    fig, (ax, ax_vol) = plt.subplots(2, 1, figsize=(10, 6),sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    def animate(i):
        """
        This sub-function runs every 1 second (1000ms).
        It clears the old drawing and draws the updated data.
        """
        ax.clear()
        ax_vol.clear()

        # We only show the last 10 candles so the chart is zoomed in and clear
        data_to_plot = candlestick.data.tail(PLOT_WINDOW)

        mpf.plot(
            data_to_plot,
            type='candle',
            style='charles',    # Green and Red classic colors
            ax=ax,
            volume=ax_vol,
            ylabel='Price'
        )

        ax.set_title(f'{SYMBOL} Real-Time Candlestick Chart')
    
    # Start the animation loop
    ani = FuncAnimation(
        fig,
        animate,
        interval=1000,
        cache_frame_data=False
    )

    plt.show()

# ============================================================
# Candlestick Class to Manage State and WebSocket Callbacks
# ============================================================
class Candlestick:
    """
    Maintains real-time OHLCV candle state using websocket ticks.

    The class receives live tick data from Fyers websocket callbacks
    and continuously updates the in-memory candle dataframe.
    """
    # ============================================================
    # Initialization
    # ============================================================
    def __init__(self, data):
        """
        Initializes the Candlestick class.
        """
        self.data = data
        self.last_total_volume = None


    # ============================================================
    # WebSocket Callback to Handle Incoming Messages
    # ============================================================
    def onmessage(self, message):
        """
        Callback function to handle incoming messages from the FyersDataSocket WebSocket.

        Parameters:
            message (dict): The received message from the WebSocket.

        """
        print(message)
        self.data, self.last_total_volume = update_live_data(data=self.data, message=message, last_total_volume=self.last_total_volume)
        print(self.data.tail(1))


    # ============================================================
    # Websocket Callback to Handle Errors Events
    # ============================================================
    def onerror(self, message):
        """
        Callback function to handle WebSocket errors.

        Parameters:
            message (dict): The error message received from the WebSocket.


        """
        print("Error:", message)


    # ============================================================
    # Websocket Callback to Handle Connection Close Events
    # ============================================================
    def onclose(self, message):
        """
        Callback function to handle WebSocket connection close events.
        """
        print("Connection closed:", message)


    # ============================================================
    # Websocket Callback to Handle Subscription Upon Connection
    # ============================================================
    def onopen(self):
        """
        Callback function to subscribe to data type and symbols upon WebSocket connection.

        """
        # Specify the data type and symbols you want to subscribe to
        data_type = "SymbolUpdate"

        # Subscribe to the specified symbols and data type
        symbols = [SYMBOL]
        fyersSocket.subscribe(symbols=symbols, data_type=data_type)

        # Keep the socket running to receive real-time data
        fyersSocket.keep_running()

# ============================================================
# STARTING THE PROGRAM
# ============================================================
if __name__ == "__main__":
    # 1. Read your secret keys (Like a password for the stock market)
    try:
        with open('access_token.txt', 'r') as file:
            access_token = file.read()
    except FileNotFoundError:
        print("Error: access_token.txt not found! Please login first.")
        exit()

    # 2. Fetch data from earlier today
    print("Fetching morning data...")
    fyers_connection = fyersModel.FyersModel(client_id=client_id, token=access_token, is_async=False, log_path='')
    historical_df = fetch_historical_data(fyers=fyers_connection)

    # 3. Initialize our data manager
    candlestick = Candlestick(historical_df)

    # 4. Create a FyersDataSocket instance with the provided parameters
    fyersSocket = data_ws.FyersDataSocket(
        access_token=access_token,          # Access token in the format "appid:accesstoken"
        log_path="",                        # Path to save logs. Leave empty to auto-create logs in the current directory.
        litemode=False,                     # Lite mode disabled. Set to True if you want a lite response.
        write_to_file=False,                # Save response in a log file instead of printing it.
        reconnect=True,                     # Enable auto-reconnection to WebSocket on disconnection.
        on_connect=candlestick.onopen,      # Callback function to subscribe to data upon connection.
        on_close=candlestick.onclose,       # Callback function to handle WebSocket connection close events.
        on_error=candlestick.onerror,       # Callback function to handle WebSocket errors.
        on_message=candlestick.onmessage    # Callback function to handle incoming messages from the WebSocket.
    )

    # 5. Establish a connection to the Fyers WebSocket
    print("Connecting to live stream...")
    fyersSocket.connect()

    # 6. Plot the chart
    try:
        plot_chart(candlestick)
    finally:
        fyersSocket.close_connection()