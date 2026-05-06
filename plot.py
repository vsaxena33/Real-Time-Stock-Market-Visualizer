# ============================================================
# Imports
# ============================================================
import matplotlib.pyplot as plt
import mplfinance as mpf
from matplotlib.animation import FuncAnimation
import configuration as config

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
        data_to_plot = candlestick.data.tail(config.plot_window)

        mpf.plot(
            data_to_plot,
            type='candle',
            style='charles',    # Green and Red classic colors
            ax=ax,
            volume=ax_vol,
            ylabel='Price'
        )

        ax.set_title(f'{config.symbol} Real-Time Candlestick Chart')
    
    # Start the animation loop
    ani = FuncAnimation(
        fig,
        animate,
        interval=1000,
        cache_frame_data=False
    )

    plt.show()
