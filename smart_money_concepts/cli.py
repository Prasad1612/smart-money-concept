import asyncio
import argparse
from typing import List
from .smc import SmartMoneyConcepts

async def main(stock_codes: List[str], period: str = "1y", interval: str = "1d", 
               batch_size: int = 10, delay: float = 2.0, visualize: bool = True):
    for i, stock_code in enumerate(stock_codes):
        print(f"\n==============================")
        print(f"🔍 Analyzing stock: {stock_code}")
        print(f"==============================")

        smc = SmartMoneyConcepts(stock_code=stock_code, period=period, interval=interval)
        
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
                        smc.print_analysis_summary()
                    break
                else:
                    print(f"❌ Analysis failed for {stock_code}!")
                    break
            except Exception as e:
                if "429" in str(e):
                    print(f"Rate limit hit for {stock_code}. Retrying ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(5)
                else:
                    print(f"Error for {stock_code}: {e}")
                    break
            if attempt == max_retries - 1:
                print(f"❌ Failed to fetch data for {stock_code} after {max_retries} attempts.")

        if (i + 1) % batch_size == 0 and i + 1 < len(stock_codes):
            print(f"Pausing for {delay} seconds after processing {batch_size} stocks...")
            await asyncio.sleep(delay)

def cli():
    parser = argparse.ArgumentParser(description="Smart Money Concepts Analysis")
    parser.add_argument(
        "--stocks",
        nargs="+",
        default=["^NSEI"],
        help="List of stock codes (e.g., '^NSEI', 'RELIANCE.NS')",
    )
    parser.add_argument(
        "--period",
        default="1y",
        help="Period for data (e.g., '1d', '1mo', '1y', 'max')",
    )
    parser.add_argument(
        "--interval",
        default="1d",
        help="Interval for data (e.g., '1m', '1h', '1d')",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of stocks to process before pausing",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay (seconds) between batches",
    )
    parser.add_argument(
        "--no-visualize",
        action="store_false",
        dest="visualize",
        help="Disable visualization",
    )
    args = parser.parse_args()
    
    asyncio.run(
        main(
            stock_codes=args.stocks,
            period=args.period,
            interval=args.interval,
            batch_size=args.batch_size,
            delay=args.delay,
            visualize=args.visualize,
        )
    )

if __name__ == "__main__":
    cli()