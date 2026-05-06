# ============================================================
# Imports
# ============================================================
import pandas as pd
import configuration as config

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
    timestamp = pd.Timestamp.now(tz=config.timeZone).floor('1min')

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
        data = data.tail(config.max_candles)                   # Keep only the last MAX_CANDLES candles to limit memory usage
        data = pd.concat([data, new_candle])

    return data, total_vol

