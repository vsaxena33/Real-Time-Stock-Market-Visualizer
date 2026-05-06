# Real-Time Stock Market Visualizer

A real-time stock market visualization tool built using the Fyers WebSocket API and Python.

This application:
- Fetches historical OHLCV (Open, High, Low, Close, Volume) market data
- Streams real-time live market ticks
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
```

---

# 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
pandas
matplotlib
mplfinance
pytz
fyers-apiv3
```

---

# 🔑 API Setup

To run this project you need:
- A Fyers trading account
- API credentials
- Access token

Generate the access token using:

```bash
python autoLogin.py
```

> Note: Due to SEBI guidelines, a new access token must be generated daily.

---

# ▶️ Running the Program

Run:

```bash
python candlestick.py
```

The application will:
- Fetch historical market data
- Connect to the live WebSocket stream
- Open a real-time updating candlestick chart

---

# 🧠 How Volume Reconstruction Works

The WebSocket feed provides:
- Total traded volume for the entire trading session

However, candlestick charts require:
- Volume traded during each candle interval

This project reconstructs candle volume using:

```text
Incremental Volume = Current Total Volume - Previous Total Volume
```

This is similar to how professional market data systems process exchange feeds.

---

# ⏱ Timeframe

Current configuration:
- 1-minute candles

Can be extended to:
- 5-minute candles
- 15-minute candles
- Hourly candles
- Daily candles

> Note: Refer to Fyers API documentation for supported resolutions.

---

# 📊 Example Use Cases

- Real-time market monitoring
- Algorithmic trading dashboards
- Market microstructure analysis
- Quantitative finance projects
- Trading strategy visualization
- Educational demonstrations

---

# ⚠️ Important Notes

- Internet connection is required
- Market must be open for live updates
- Access tokens expire periodically
- Designed primarily for educational and visualization purposes

---

# 🚀 Future Improvements

Potential upgrades:
- Technical indicators (EMA, VWAP, RSI)
- Multi-timeframe charts
- Persistent database storage
- Multi-symbol support
- GUI improvements
- Thread-safe architecture
- Strategy backtesting integration
- Order book visualization

---

# 👨‍💻 Author

Vaibhav Saxena

---

# 📜 License

This project is intended for educational and personal use.
