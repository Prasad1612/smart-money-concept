# 📈 Smart Money Concepts (SMC) in Python  

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)  
![yfinance](https://img.shields.io/badge/yfinance-0.2.40+-brightgreen.svg)  
![pandas](https://img.shields.io/badge/pandas-2.0+-yellow.svg)  
![matplotlib](https://img.shields.io/badge/matplotlib-3.7+-orange.svg)  

A Python package for performing **Smart Money Concepts (SMC)** technical analysis using historical stock data from **yfinance**.  
This framework helps traders and analysts detect **market structure, order blocks, fair value gaps, BOS/CHoCH**, and visualize them with **matplotlib**.  

---

## 🚀 Features  
✅ **Market Structure Analysis** — Break of Structure (BOS) & Change of Character (CHoCH)  
✅ **Order Blocks** — Bullish & Bearish institutional zones  
✅ **Fair Value Gaps (FVG)** — Detection with mitigation logic  
✅ **Equal Highs & Lows (EQH/EQL)** — Potential reversal points  
✅ **Premium & Discount Zones** — Dynamic equilibrium mapping  
✅ **Visualization** — Candlestick charts with SMC overlays  
✅ **Real-time Data** — Fetches from Yahoo Finance  
✅ **CLI Support** — Batch run multiple stocks  

---

## ⚙️ Installation  

From **PyPI**:  
```bash
pip install smart-money-concept
```

From **Source**:  
```bash
git clone https://github.com/Prasad1612/smart-money-concept.git
cd smart-money-concept

# Install dependencies
pip install -r requirements.txt

# Install locally
pip install .
```

---

## 🧑‍💻 Usage  

### Python Script Example  
```python
import asyncio
from typing import List, Dict
from smart_money_concepts import SmartMoneyConcepts

async def main(stock_codes: List[str], period: str = "max", interval: str = "1d", batch_size: int = 10, delay: float = 2.0, visualize: bool = True):
    if not stock_codes:
        stock_codes = ["RELIANCE.NS"]  # Default to NSE-listed Reliance

    for i, stock_code in enumerate(stock_codes):
        print(f"\n==============================")
        print(f"🔍 Analyzing stock: {stock_code}")
        print(f"==============================")

        smc = SmartMoneyConcepts(stock_code=stock_code, period=period, interval=interval)
        
        # Retry logic for fetching data
        max_retries = 3
        for attempt in range(max_retries):
            try:
                success = await smc.fetch_ohlcv()
                if success:
                    smc.prepare_data()
                    smc.run_smc_analysis()
                    if visualize:
                        smc.visualize_smc(bars_to_show=500)
                    else:
                        smc.print_analysis_summary()  # Print summary even if visualization is skipped
                    break
                else:
                    print(f"❌ Analysis failed for {stock_code}!")
                    break
            except Exception as e:
                if "429" in str(e):  # Check for rate limit error
                    print(f"Rate limit hit for {stock_code}. Retrying ({attempt + 1}/{max_retries}) after delay...")
                    await asyncio.sleep(5)  # Wait longer for rate limit errors
                else:
                    print(f"Error for {stock_code}: {e}")
                    break
            if attempt == max_retries - 1:
                print(f"❌ Failed to fetch data for {stock_code} after {max_retries} attempts.")

        # Add delay after every batch_size stocks
        if (i + 1) % batch_size == 0 and i + 1 < len(stock_codes):
            print(f"Pausing for {delay} seconds after processing {batch_size} stocks...")
            await asyncio.sleep(delay)

if __name__ == "__main__":
    # Example stock list (use .NS for NSE-listed stocks, .BO for BSE, or others as needed)

    # Stocks
    stock_codes = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    
    # Index
    # stock_codes = ["^NSEI"]
    
    asyncio.run(main(stock_codes, period="1y", interval="1d", batch_size=10, delay=2.0, visualize=True))
```

### CLI Example  
```bash
python -m smart_money_concepts.cli --stocks ^NSEI RELIANCE.NS --period 1y --interval 1d
```

Options:  
- `--stocks`: List of stock codes (default: RELIANCE.NS)  
- `--period`: Data period (default: 1y)  
- `--interval`: Data interval (default: 1d)  
- `--batch-size`: Number of stocks before pause (default: 10)  
- `--delay`: Delay between batches (default: 2.0s)  
- `--no-visualize`: Only print summary  

---

## 📊 Example Output  
- BOS / CHoCH markers on swing structures  
- Bullish & Bearish Order Blocks  
- Fair Value Gaps (highlighted)  
- Equal Highs & Equal Lows  
- Premium / Discount zones  

*(Sample visualization screenshots recommended here)*  

---

## 📂 Project Structure  
```
smart-money-concepts/
├── smart_money_concepts/
│   ├── __init__.py
│   ├── smc.py
│   ├── cli.py
├── README.md
├── requirements.txt
```

---

## 🙌 Credits  
- **[Code Tech (YouTube)](https://www.youtube.com/watch?v=s6YWq-W7V6g)** → Tutorial on building an SMC indicator in Python  
- **[LuxAlgo](https://www.luxalgo.com/library/indicator/smart-money-concepts-smc/)** → Inspiration from their Smart Money Concepts indicator  

---

## ⚠️ Notes  
- Uses `yfinance`, subject to rate limits (retry logic included).  
- Requires an active internet connection.  
- **Disclaimer**: Educational purposes only — not financial advice.  

---

## 📬 Contact  
For questions, open an **Issue** on GitHub.  

---


