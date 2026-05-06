# Real-Time Stock Market Visualizer

A real-time stock market visualization tool built using the Fyers WebSocket API and Python.

This application fetches:
- Historical OHLCV (Open, High, Low, Close, Volume) market data
- Real-time live market ticks
- Dynamically updates candlestick charts in real-time

The project demonstrates:
- Real-time market data streaming
- Candlestick generation from live ticks
- Volume reconstruction using cumulative exchange volume
- Financial data visualization using Python

---

# 📈 What is a Candlestick Chart?

A candlestick chart is one of the most commonly used chart types in financial markets.

Each candle represents price activity over a fixed interval of time (1 minute in this project).

A single candle contains:

| Component | Meaning |
|---|---|
| Open | Price at the beginning of the interval |
| High | Highest traded price during the interval |
| Low | Lowest traded price during the interval |
| Close | Price at the end of the interval |
| Volume | Number of shares/contracts traded |

Candlestick charts help traders visualize:
- Market trends
- Momentum
- Volatility
- Reversal patterns
- Buying/Selling pressure

---

# ⚡ Features

- Real-time WebSocket-based market updates
- Historical + live data synchronization
- Dynamic candlestick creation
- Real-time volume bars
- Automatic candle updates every second
- Timezone-aware timestamps (IST)
- Memory-efficient rolling candle window
- Live matplotlib animation

---

# 🛠 Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data manipulation |
| Matplotlib | Plotting engine |
| mplfinance | Financial charting |
| Fyers API v3 | Market data access |
| WebSocket | Real-time streaming |
| pytz | Timezone handling |

---

# 📂 Project Structure

```text
project/
│
├── candlestick.py
├── credentials.py
├── autoLogin.py
├── requirements.txt
└── README.md
