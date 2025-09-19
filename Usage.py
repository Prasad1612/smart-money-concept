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