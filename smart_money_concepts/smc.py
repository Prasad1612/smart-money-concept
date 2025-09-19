import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
import warnings
import os
warnings.filterwarnings('ignore')

# Data structures (unchanged from original)
class Alerts:
    def __init__(self):
        self.internal_bullish_bos = False
        self.internal_bearish_bos = False
        self.internal_bullish_choch = False
        self.internal_bearish_choch = False
        self.swing_bullish_bos = False
        self.swing_bearish_bos = False
        self.swing_bullish_choch = False
        self.swing_bearish_choch = False
        self.internal_bullish_order_block = False
        self.internal_bearish_order_block = False
        self.swing_bullish_order_block = False
        self.swing_bearish_order_block = False
        self.equal_highs = False
        self.equal_lows = False
        self.bullish_fair_value_gap = False
        self.bearish_fair_value_gap = False

class TrailingExtremes:
    def __init__(self):
        self.top = None
        self.bottom = None
        self.bar_time = None
        self.bar_index = None
        self.last_top_time = None
        self.last_bottom_time = None

class FairValueGap:
    def __init__(self, top: float, bottom: float, bias: int, start_time: int = None,
                 end_time: int = None, start_idx: int = None, width: int = 0):
        self.top = top
        self.bottom = bottom
        self.bias = bias
        self.start_time = start_time
        self.end_time = end_time
        self.start_idx = start_idx
        self.width = width
        self.top_box = None
        self.bottom_box = None

class Trend:
    def __init__(self, bias: int = 0):
        self.bias = bias

class EqualDisplay:
    def __init__(self):
        self.line = None
        self.label = None

class Pivot:
    def __init__(self, current_level: float = None, last_level: float = None,
                 crossed: bool = False, bar_time: int = None, bar_index: int = None):
        self.current_level = current_level
        self.last_level = last_level
        self.crossed = crossed
        self.bar_time = bar_time
        self.bar_index = bar_index

class OrderBlock:
    def __init__(self, bar_high: float, bar_low: float, bar_time: int, bias: int):
        self.bar_high = bar_high
        self.bar_low = bar_low
        self.bar_time = bar_time
        self.bias = bias

class SmartMoneyConcepts:
    def __init__(self, stock_code: str, period: str = "1y", interval: str = "1d"):
        """Smart Money Concepts Indicator - Python Implementation using yfinance data.

        Args:
            stock_code (str): Stock ticker symbol (e.g., 'RELIANCE.NS' for NSE).
            period (str): Period for yfinance data (e.g., '1y' for 1 year).
            interval (str): Interval for yfinance data (e.g., '1d' for daily).
        """
        self.stock_code = stock_code
        self.period = period
        self.interval = interval

        # Initialize data containers
        self.df = None
        self.ohlcv_data = None

        # Initialize the indicator
        self.setup_constants()
        self.setup_variables()

    def setup_constants(self):
        # Same as original
        self.BULLISH_LEG = 1
        self.BEARISH_LEG = 0
        self.BULLISH = 1
        self.BEARISH = -1
        self.GREEN = '#089981'
        self.RED = '#F23645'
        self.BLUE = '#2157f3'
        self.GRAY = '#878b94'
        self.MONO_BULLISH = '#b2b5be'
        self.MONO_BEARISH = '#5d606b'
        self.HISTORICAL = 'Historical'
        self.PRESENT = 'Present'
        self.COLORED = 'Colored'
        self.MONOCHROME = 'Monochrome'
        self.ALL = 'All'
        self.BOS = 'BOS'
        self.CHOCH = 'CHOCH'
        self.ATR = 'Atr'
        self.RANGE = 'Cumulative Mean Range'
        self.CLOSE = 'Close'
        self.HIGHLOW = 'High/Low'
        self.mode_input = self.HISTORICAL
        self.style_input = self.COLORED
        self.show_trend_input = False
        self.show_internals_input = True
        self.show_internal_bull_input = self.ALL
        self.internal_bull_color_input = self.GREEN
        self.show_internal_bear_input = self.ALL
        self.internal_bear_color_input = self.RED
        self.internal_filter_confluence_input = False
        self.show_structure_input = True
        self.show_swing_bull_input = self.ALL
        self.swing_bull_color_input = self.GREEN
        self.show_swing_bear_input = self.ALL
        self.swing_bear_color_input = self.RED
        self.show_swings_input = False
        self.swings_length_input = 50
        self.show_high_low_swings_input = True
        self.show_internal_order_blocks_input = True
        self.internal_order_blocks_size_input = 5
        self.show_swing_order_blocks_input = True
        self.swing_order_blocks_size_input = 5
        self.order_block_filter_input = self.ATR
        self.order_block_mitigation_input = self.HIGHLOW
        self.internal_bullish_order_block_color = "#3179f580"
        self.internal_bearish_order_block_color = "#f77c8080"
        self.swing_bullish_order_block_color = "#1848cc80"
        self.swing_bearish_order_block_color = "#b2283380"
        self.show_equal_highs_lows_input = True
        self.equal_highs_lows_length_input = 3
        self.equal_highs_lows_threshold_input = 0.1
        self.show_fair_value_gaps_input = True
        self.fair_value_gaps_threshold_input = True
        self.fair_value_gaps_timeframe_input = ''
        self.fair_value_gaps_bull_color_input = "#00ff6870"
        self.fair_value_gaps_bear_color_input = "#ff000870"
        self.fair_value_gaps_extend_input = 5
        self.show_premium_discount_zones_input = True
        self.premium_zone_color_input = self.RED
        self.equilibrium_zone_color_input = self.GRAY
        self.discount_zone_color_input = self.GREEN

    def setup_variables(self):
        # Same as original
        self.parsed_highs = []
        self.parsed_lows = []
        self.highs = []
        self.lows = []
        self.times = []
        self.swing_high = Pivot()
        self.swing_low = Pivot()
        self.internal_high = Pivot()
        self.internal_low = Pivot()
        self.equal_high = Pivot()
        self.equal_low = Pivot()
        self.swing_trend = Trend(0)
        self.internal_trend = Trend(0)
        self.equal_high_display = EqualDisplay()
        self.equal_low_display = EqualDisplay()
        self.fair_value_gaps = []
        self.swing_order_blocks = []
        self.internal_order_blocks = []
        self.trailing = TrailingExtremes()
        self.current_bar_index = 0
        self.last_bar_index = 0
        self.current_alerts = Alerts()
        self.initial_time = None
        self.swing_bullish_color = self.MONO_BULLISH if self.style_input == self.MONOCHROME else self.swing_bull_color_input
        self.swing_bearish_color = self.MONO_BEARISH if self.style_input == self.MONOCHROME else self.swing_bear_color_input
        self.fair_value_gap_bullish_color = f"{self.MONO_BULLISH}70" if self.style_input == self.MONOCHROME else self.fair_value_gaps_bull_color_input
        self.fair_value_gap_bearish_color = f"{self.MONO_BEARISH}70" if self.style_input == self.MONOCHROME else self.fair_value_gaps_bear_color_input
        self.premium_zone_color = self.MONO_BEARISH if self.style_input == self.MONOCHROME else self.premium_zone_color_input
        self.discount_zone_color = self.MONO_BULLISH if self.style_input == self.MONOCHROME else self.discount_zone_color_input

    async def fetch_ohlcv(self):
        """Fetch OHLCV data using yfinance."""
        try:
            print(f"Fetching data for {self.stock_code} using yfinance...")
            # Download data using yfinance
            ticker = yf.Ticker(self.stock_code)
            self.df = ticker.history(period=self.period, interval=self.interval)

            # Ensure required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close']
            if not all(col in self.df.columns for col in required_columns):
                print(f"Data for {self.stock_code} missing required columns: {required_columns}")
                return False

            # Map yfinance columns to match the expected format
            column_mapping = {
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close'
            }
            self.df = self.df.rename(columns=column_mapping)

            # Ensure timestamp is in datetime format and set as index
            self.df.index = pd.to_datetime(self.df.index)
            self.df = self.df.sort_index()  # Sort by date (oldest to newest)

            # Drop rows with missing data
            self.df = self.df.dropna(subset=['open', 'high', 'low', 'close'])

            # Store OHLCV data
            self.ohlcv_data = self.df[['open', 'high', 'low', 'close']].copy()
            print(f"Successfully fetched {len(self.df)} bars")
            print(f"Data range: {self.df.index[0].date()} to {self.df.index[-1].date()}")
            return True

        except Exception as e:
            print(f"Error fetching data for {self.stock_code}: {e}")
            return False

    def prepare_data(self):
        # Same as original
        if self.df is None:
            raise ValueError("No data available. Please fetch data first.")

        self.df['tr'] = np.maximum(
            self.df['high'] - self.df['low'],
            np.maximum(
                abs(self.df['high'] - self.df['close'].shift(1)),
                abs(self.df['low'] - self.df['close'].shift(1))
            )
        )
        self.df['atr'] = self.df['tr'].rolling(window=200, min_periods=1).mean()
        self.df['volatility_measure'] = self.df['atr'] if self.order_block_filter_input == self.ATR else self.df['tr'].expanding().mean()
        self.df['high_volatility_bar'] = (self.df['high'] - self.df['low']) >= (2 * self.df['volatility_measure'])
        self.df['parsed_high'] = np.where(self.df['high_volatility_bar'], self.df['low'], self.df['high'])
        self.df['parsed_low'] = np.where(self.df['high_volatility_bar'], self.df['high'], self.df['low'])
        self.highs = self.df['high'].values
        self.lows = self.df['low'].values
        self.parsed_highs = self.df['parsed_high'].values
        self.parsed_lows = self.df['parsed_low'].values
        self.times = self.df.index.values
        self.initial_time = self.times[0]
        # print("Data preparation completed")

    # The rest of the methods (leg, get_current_structure, etc.) remain unchanged
    # Including only the necessary methods for brevity, assuming they are the same as in the original code

    def leg(self, size: int, current_bar: int) -> int:
        if not hasattr(self, "_leg_vars"):
            self._leg_vars = {}
        if size not in self._leg_vars:
            self._leg_vars[size] = 0

        if current_bar < size:
            return self._leg_vars[size]

        high_size_ago = self.highs[current_bar - size]
        low_size_ago = self.lows[current_bar - size]
        highest_high = np.max(self.highs[current_bar - size + 1: current_bar + 1])
        lowest_low = np.min(self.lows[current_bar - size + 1: current_bar + 1])
        new_leg_high = high_size_ago > highest_high
        new_leg_low = low_size_ago < lowest_low

        if new_leg_high:
            self._leg_vars[size] = self.BEARISH_LEG
        elif new_leg_low:
            self._leg_vars[size] = self.BULLISH_LEG

        return self._leg_vars[size]

    def get_current_structure(self, size: int, equal_high_low: bool = False, internal: bool = False):
        if not hasattr(self, '_prev_legs'):
            self._prev_legs = {}
        if size not in self._prev_legs:
            self._prev_legs[size] = []

        for current_bar in range(len(self.highs)):
            current_leg = self.leg(size, current_bar)
            if len(self._prev_legs[size]) == 0:
                previous_leg = 0
            else:
                previous_leg = self._prev_legs[size][-1]
            self._prev_legs[size].append(current_leg)
            leg_change = current_leg - previous_leg
            new_pivot = leg_change != 0
            pivot_low = leg_change == 1
            pivot_high = leg_change == -1

            if new_pivot:
                if pivot_low:
                    if equal_high_low:
                        pivot_obj = self.equal_low
                    elif internal:
                        pivot_obj = self.internal_low
                    else:
                        pivot_obj = self.swing_low

                    if current_bar >= size:
                        low_value = self.lows[current_bar - size]
                        time_value = self.times[current_bar - size]
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[min(current_bar, len(self.df) - 1)]['atr']
                            if abs(pivot_obj.current_level - low_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low(pivot_obj, low_value, size, False, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = low_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.bottom = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_bottom_time = pivot_obj.bar_time

                elif pivot_high:
                    if equal_high_low:
                        pivot_obj = self.equal_high
                    elif internal:
                        pivot_obj = self.internal_high
                    else:
                        pivot_obj = self.swing_high

                    if current_bar >= size:
                        high_value = self.highs[current_bar - size]
                        time_value = self.times[current_bar - size]
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[min(current_bar, len(self.df) - 1)]['atr']
                            if abs(pivot_obj.current_level - high_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low(pivot_obj, high_value, size, True, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = high_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.top = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_top_time = pivot_obj.bar_time

    def draw_equal_high_low(self, pivot_obj: Pivot, level: float, size: int, equal_high: bool, index: int):
        equal_data = {
            "type": "EQH" if equal_high else "EQL",
            "start_time": pivot_obj.bar_time,
            "start_level": pivot_obj.current_level,
            "end_time": self.times[index],
            "end_level": level,
            "color": self.swing_bearish_color if equal_high else self.swing_bullish_color,
        }
        if not hasattr(self, "equal_structures"):
            self.equal_structures = []
        self.equal_structures.append(equal_data)
        if equal_high:
            self.current_alerts.equal_highs = True
        else:
            self.current_alerts.equal_lows = True

    def delete_order_blocks(self, internal: bool = False):
        order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
        bearish_mitigation_source = self.df['close'] if self.order_block_mitigation_input == self.CLOSE else self.df['high']
        bullish_mitigation_source = self.df['close'] if self.order_block_mitigation_input == self.CLOSE else self.df['low']
        blocks_to_remove = []
        for i, order_block in enumerate(order_blocks):
            crossed_order_block = False
            if order_block.bias == 'BEARISH':
                if bearish_mitigation_source.iloc[-1] > order_block.bar_high:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bearish_order_block = True
                    else:
                        self.current_alerts.swing_bearish_order_block = True
            elif order_block.bias == 'BULLISH':
                if bullish_mitigation_source.iloc[-1] < order_block.bar_low:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bullish_order_block = True
                    else:
                        self.current_alerts.swing_bullish_order_block = True
            if crossed_order_block:
                blocks_to_remove.append(i)
        for i in reversed(blocks_to_remove):
            order_blocks.pop(i)

    def store_order_block(self, pivot_obj, internal: bool = False, bias: int = None):
        if (not internal and self.show_swing_order_blocks_input) or (internal and self.show_internal_order_blocks_input):
            if bias == self.BEARISH:
                start_idx = max(0, pivot_obj.bar_index)
                end_idx = min(len(self.parsed_highs), len(self.highs))
                if start_idx < end_idx:
                    slice_highs = self.parsed_highs[start_idx:end_idx]
                    if len(slice_highs) > 0:
                        max_idx = np.argmax(slice_highs)
                        parsed_index = start_idx + max_idx
                    else:
                        parsed_index = start_idx
                else:
                    parsed_index = start_idx
            else:
                start_idx = max(0, pivot_obj.bar_index)
                end_idx = min(len(self.parsed_lows), len(self.lows))
                if start_idx < end_idx:
                    slice_lows = self.parsed_lows[start_idx:end_idx]
                    if len(slice_lows) > 0:
                        min_idx = np.argmin(slice_lows)
                        parsed_index = start_idx + min_idx
                    else:
                        parsed_index = start_idx
                else:
                    parsed_index = start_idx
            if parsed_index < len(self.parsed_highs) and parsed_index < len(self.parsed_lows):
                order_block = OrderBlock(
                    bar_high=self.parsed_highs[parsed_index],
                    bar_low=self.parsed_lows[parsed_index],
                    bar_time=self.times[parsed_index],
                    bias=bias
                )
                order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
                if len(order_blocks) >= 100:
                    order_blocks.pop()
                order_blocks.insert(0, order_block)

    def display_structure(self, internal: bool = False):
        bullish_bar = True
        bearish_bar = True
        for i in range(1, len(self.df)):
            current_close = self.df.iloc[i]['close']
            current_open = self.df.iloc[i]['open']
            current_high = self.df.iloc[i]['high']
            current_low = self.df.iloc[i]['low']
            previous_close = self.df.iloc[i - 1]['close']
            if self.internal_filter_confluence_input:
                bullish_bar = (current_high - max(current_close, current_open)) > min(current_close, current_open - current_low)
                bearish_bar = (current_high - max(current_close, current_open)) < min(current_close, current_open - current_low)
            pivot_high = self.internal_high if internal else self.swing_high
            trend_obj = self.internal_trend if internal else self.swing_trend
            if (pivot_high.current_level is not None and
                current_close > pivot_high.current_level and
                previous_close <= pivot_high.current_level and
                not pivot_high.crossed):
                extra_condition = True
                if internal:
                    extra_condition = (pivot_high.current_level != self.swing_high.current_level and bullish_bar)
                if extra_condition:
                    tag = self.CHOCH if trend_obj.bias == self.BEARISH else self.BOS
                    if internal:
                        self.current_alerts.internal_bullish_choch = (tag == self.CHOCH)
                        self.current_alerts.internal_bullish_bos = (tag == self.BOS)
                    else:
                        self.current_alerts.swing_bullish_choch = (tag == self.CHOCH)
                        self.current_alerts.swing_bullish_bos = (tag == self.BOS)
                    pivot_high.crossed = True
                    trend_obj.bias = self.BULLISH
                    structure_data = {
                        'type': tag,
                        'bias': self.BULLISH,
                        'level': pivot_high.current_level,
                        'time': pivot_high.bar_time,
                        'break_time': self.times[i],
                        'color': self.swing_bullish_color,
                        'internal': internal
                    }
                    if not hasattr(self, 'structure_breaks'):
                        self.structure_breaks = []
                    self.structure_breaks.append(structure_data)
                    if (internal and self.show_internal_order_blocks_input) or (not internal and self.show_swing_order_blocks_input):
                        self.store_order_block(pivot_high, internal, self.BULLISH)
            pivot_low = self.internal_low if internal else self.swing_low
            if (pivot_low.current_level is not None and
                current_close < pivot_low.current_level and
                previous_close >= pivot_low.current_level and
                not pivot_low.crossed):
                extra_condition = True
                if internal:
                    extra_condition = (pivot_low.current_level != self.swing_low.current_level and bearish_bar)
                if extra_condition:
                    tag = self.CHOCH if trend_obj.bias == self.BULLISH else self.BOS
                    if internal:
                        self.current_alerts.internal_bearish_choch = (tag == self.CHOCH)
                        self.current_alerts.internal_bearish_bos = (tag == self.BOS)
                    else:
                        self.current_alerts.swing_bearish_choch = (tag == self.CHOCH)
                        self.current_alerts.swing_bearish_bos = (tag == self.BOS)
                    pivot_low.crossed = True
                    trend_obj.bias = self.BEARISH
                    structure_data = {
                        'type': tag,
                        'bias': self.BEARISH,
                        'level': pivot_low.current_level,
                        'time': pivot_low.bar_time,
                        'break_time': self.times[i],
                        'color': self.swing_bearish_color,
                        'internal': internal
                    }
                    if not hasattr(self, 'structure_breaks'):
                        self.structure_breaks = []
                    self.structure_breaks.append(structure_data)
                    if (internal and self.show_internal_order_blocks_input) or (not internal and self.show_swing_order_blocks_input):
                        self.store_order_block(pivot_low, internal, self.BEARISH)

    def delete_fair_value_gaps(self):
        gaps_to_remove = []
        current_high = self.df.iloc[-1]['high']
        current_low = self.df.iloc[-1]['low']
        for i, gap in enumerate(self.fair_value_gaps):
            if gap.bias == self.BULLISH and current_low < gap.bottom:
                gaps_to_remove.append(i)
            elif gap.bias == self.BEARISH and current_high > gap.top:
                gaps_to_remove.append(i)
        for idx in reversed(gaps_to_remove):
            self.fair_value_gaps.pop(idx)

    def detect_fair_value_gaps(self):
        if not self.show_fair_value_gaps_input:
            return
        for i in range(2, len(self.df)):
            current_high = self.highs[i]
            current_low = self.lows[i]
            last_high = self.highs[i - 1]
            last_low = self.lows[i - 1]
            last_close = self.df.iloc[i - 1]['close']
            last_open = self.df.iloc[i - 1]['open']
            last2_high = self.highs[i - 2]
            last2_low = self.lows[i - 2]
            bar_delta_percent = (last_close - last_open) / last_open if last_open != 0 else 0
            threshold = abs(bar_delta_percent) * 2 if self.fair_value_gaps_threshold_input else 0
            bullish_fvg = (current_low > last2_high and
                           last_close > last2_high and
                           bar_delta_percent > threshold)
            bearish_fvg = (current_high < last2_low and
                           last_close < last2_low and
                           -bar_delta_percent > threshold)
            if bullish_fvg:
                self.current_alerts.bullish_fair_value_gap = True
                fvg = FairValueGap(
                    top=current_low,
                    bottom=last2_high,
                    bias=self.BULLISH
                )
                self.fair_value_gaps.insert(0, fvg)
            elif bearish_fvg:
                self.current_alerts.bearish_fair_value_gap = True
                fvg = FairValueGap(
                    top=current_high,
                    bottom=last2_low,
                    bias=self.BEARISH
                )
                self.fair_value_gaps.insert(0, fvg)

    def update_trailing_extremes(self):
        for i in range(len(self.df)):
            current_high = self.highs[i]
            current_low = self.lows[i]
            if self.trailing.top is None or current_high > self.trailing.top:
                self.trailing.top = current_high
                self.trailing.last_top_time = self.times[i]
            if self.trailing.bottom is None or current_low < self.trailing.bottom:
                self.trailing.bottom = current_low
                self.trailing.last_bottom_time = self.times[i]

    def calculate_premium_discount_zones(self):
        if not self.show_premium_discount_zones_input:
            return
        if self.trailing.top is None or self.trailing.bottom is None:
            return
        premium_top = self.trailing.top
        premium_bottom = 0.95 * self.trailing.top + 0.05 * self.trailing.bottom
        equilibrium_top = 0.525 * self.trailing.top + 0.475 * self.trailing.bottom
        equilibrium_bottom = 0.525 * self.trailing.bottom + 0.475 * self.trailing.top
        discount_top = 0.95 * self.trailing.bottom + 0.05 * self.trailing.top
        discount_bottom = self.trailing.bottom
        self.premium_discount_zones = {
            'premium': {
                'top': premium_top,
                'bottom': premium_bottom,
                'color': self.premium_zone_color
            },
            'equilibrium': {
                'top': equilibrium_top,
                'bottom': equilibrium_bottom,
                'color': self.equilibrium_zone_color_input
            },
            'discount': {
                'top': discount_top,
                'bottom': discount_bottom,
                'color': self.discount_zone_color
            }
        }

    def run_smc_analysis(self):
        print("Running Smart Money Concepts analysis...")
        self.structure_breaks = []
        self.equal_structures = []
        # print("Processing bars exactly like Pine Script execution...")
        for current_bar in range(len(self.df)):
            self.current_bar_index = current_bar
            self.last_bar_index = current_bar - 1 if current_bar > 0 else 0
            self.current_bar_time = self.times[current_bar]
            current_high = self.highs[current_bar]
            current_low = self.lows[current_bar]
            current_close = self.df.iloc[current_bar]['close']
            current_open = self.df.iloc[current_bar]['open']
            atr_measure = self.df.iloc[current_bar]['atr']
            volatility_measure = atr_measure if self.order_block_filter_input == self.ATR else self.df.iloc[current_bar]['volatility_measure']
            high_volatility_bar = (current_high - current_low) >= (2 * volatility_measure)
            self.parsed_highs[current_bar] = current_low if high_volatility_bar else current_high
            self.parsed_lows[current_bar] = current_high if high_volatility_bar else current_low
            if self.order_block_filter_input or self.show_premium_discount_zones_input:
                self.update_trailing_extremes_bar(current_bar)
                if self.show_premium_discount_zones_input:
                    self.calculate_premium_discount_zones_bar(current_bar)
            if self.show_fair_value_gaps_input:
                self.delete_fair_value_gaps_bar(current_bar)
            self.get_current_structure_bar(self.swings_length_input, False, False, current_bar)
            self.get_current_structure_bar(5, False, True, current_bar)
            if self.show_equal_highs_lows_input:
                self.get_current_structure_bar(self.equal_highs_lows_length_input, True, False, current_bar)
            if self.show_internals_input or self.show_internal_order_blocks_input or self.show_trend_input:
                self.display_structure_bar(True, current_bar)
            if self.show_structure_input or self.show_swing_order_blocks_input or self.show_high_low_swings_input:
                self.display_structure_bar(False, current_bar)
            if self.show_internal_order_blocks_input:
                self.delete_order_blocks_bar(True, current_bar)
            if self.show_swing_order_blocks_input:
                self.delete_order_blocks_bar(False, current_bar)
            if self.show_fair_value_gaps_input:
                self.detect_fair_value_gaps_bar(current_bar)
            if current_bar == len(self.df) - 1:
                if self.show_internal_order_blocks_input:
                    self.draw_order_blocks_final(True)
                if self.show_swing_order_blocks_input:
                    self.draw_order_blocks_final(False)
        print("Smart Money Concepts analysis completed!")
        print("Final Results:")
        print(f"Swing high: {self.swing_high.current_level:.2f}")
        print(f"Swing low: {self.swing_low.current_level:.2f}")
        print(f"Internal high: {self.internal_high.current_level:.2f}")
        print(f"Internal low: {self.internal_low.current_level:.2f}")
        print(f"Swing trend: {self.swing_trend.bias}")
        print(f"Internal trend: {self.internal_trend.bias}")
        print(f"Structure breaks: {len(self.structure_breaks)}")
        print(f"Order blocks: {len(self.internal_order_blocks) + len(self.swing_order_blocks)}")
        print(f"Equal structures: {len(self.equal_structures)}")

    def leg_bar(self, size: int, current_bar: int) -> int:
        if not hasattr(self, "_leg_vars"):
            self._leg_vars = {}
        if size not in self._leg_vars:
            self._leg_vars[size] = 0
        if current_bar < size:
            return self._leg_vars[size]
        high_size_ago = self.highs[current_bar - size]
        low_size_ago = self.lows[current_bar - size]
        highest_high = np.max(self.highs[current_bar - size + 1: current_bar + 1])
        lowest_low = np.min(self.lows[current_bar - size + 1: current_bar + 1])
        new_leg_high = high_size_ago > highest_high
        new_leg_low = low_size_ago < lowest_low
        if new_leg_high:
            self._leg_vars[size] = self.BEARISH_LEG
        elif new_leg_low:
            self._leg_vars[size] = self.BULLISH_LEG
        return self._leg_vars[size]

    def ta_change(self, value: int, size: int, current_bar: int) -> int:
        if not hasattr(self, '_prev_values'):
            self._prev_values = {}
        key = f"{size}_{current_bar}"
        if key not in self._prev_values:
            self._prev_values[key] = value
            return 0
        prev_value = self._prev_values[key]
        self._prev_values[key] = value
        return value - prev_value

    # In get_current_structure_bar method
    def get_current_structure_bar(self, size: int, equal_high_low: bool, internal: bool, current_bar: int):
        current_leg = self.leg_bar(size, current_bar)
        if not hasattr(self, '_leg_history'):
            self._leg_history = {}
        if size not in self._leg_history:
            self._leg_history[size] = []
        if len(self._leg_history[size]) == 0:
            leg_change = 0
        else:
            leg_change = current_leg - self._leg_history[size][-1]
        self._leg_history[size].append(current_leg)
        new_pivot = leg_change != 0
        pivot_low = leg_change == 1
        pivot_high = leg_change == -1
        if new_pivot:
            if pivot_low:
                if equal_high_low:
                    pivot_obj = self.equal_low
                elif internal:
                    pivot_obj = self.internal_low
                else:
                    pivot_obj = self.swing_low
                if current_bar >= size:
                    low_value = self.lows[current_bar - size]
                    time_value = self.times[current_bar - size]
                    # Check to avoid duplicate pivot detection
                    if pivot_obj.bar_index != current_bar - size or pivot_obj.current_level != low_value:
                        # print(f"Detected pivot low at index {current_bar - size}, price {low_value:.2f}, time {time_value}")
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[current_bar]['atr']
                            if abs(pivot_obj.current_level - low_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low_bar(pivot_obj, low_value, size, False, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = low_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.bottom = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_bottom_time = pivot_obj.bar_time
            elif pivot_high:
                if equal_high_low:
                    pivot_obj = self.equal_high
                elif internal:
                    pivot_obj = self.internal_high
                else:
                    pivot_obj = self.swing_high
                if current_bar >= size:
                    high_value = self.highs[current_bar - size]
                    time_value = self.times[current_bar - size]
                    # Check to avoid duplicate pivot detection
                    if pivot_obj.bar_index != current_bar - size or pivot_obj.current_level != high_value:
                        # print(f"Detected pivot high at index {current_bar - size}, price {high_value:.2f}, time {time_value}")
                        if equal_high_low and pivot_obj.current_level is not None:
                            atr_value = self.df.iloc[current_bar]['atr']
                            if abs(pivot_obj.current_level - high_value) < self.equal_highs_lows_threshold_input * atr_value:
                                self.draw_equal_high_low_bar(pivot_obj, high_value, size, True, current_bar)
                        pivot_obj.last_level = pivot_obj.current_level
                        pivot_obj.current_level = high_value
                        pivot_obj.crossed = False
                        pivot_obj.bar_time = time_value
                        pivot_obj.bar_index = current_bar - size
                        if not equal_high_low and not internal:
                            self.trailing.top = pivot_obj.current_level
                            self.trailing.bar_time = pivot_obj.bar_time
                            self.trailing.bar_index = pivot_obj.bar_index
                            self.trailing.last_top_time = pivot_obj.bar_time

    # In display_structure_bar method
    def display_structure_bar(self, internal: bool, current_bar: int):
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_close = self.df.iloc[current_bar]['close']
        current_open = self.df.iloc[current_bar]['open']
        if not hasattr(self, '_bullish_bar'):
            self._bullish_bar = True
            self._bearish_bar = True
        if self.internal_filter_confluence_input:
            self._bullish_bar = current_high - max(current_close, current_open) > min(current_close, current_open - current_low)
            self._bearish_bar = current_high - max(current_close, current_open) < min(current_close, current_open - current_low)
        pivot_obj = self.internal_high if internal else self.swing_high
        trend_obj = self.internal_trend if internal else self.swing_trend
        extra_condition = True
        if internal:
            extra_condition = (self.internal_high.current_level != self.swing_high.current_level and self._bullish_bar)
        if (pivot_obj.current_level is not None and
            current_close > pivot_obj.current_level and
            not pivot_obj.crossed and
            extra_condition):
            if current_bar > 0:
                prev_close = self.df.iloc[current_bar - 1]['close']
                if prev_close <= pivot_obj.current_level:
                    tag = self.CHOCH if trend_obj.bias != self.BULLISH else self.BOS
                    # print(f"Bullish break at index {current_bar}, price {pivot_obj.current_level:.2f}, type {tag}, trend {trend_obj.bias}")
                    if internal:
                        if tag == self.CHOCH:
                            self.current_alerts.internal_bullish_choch = True
                        else:
                            self.current_alerts.internal_bullish_bos = True
                    else:
                        if tag == self.CHOCH:
                            self.current_alerts.swing_bullish_choch = True
                        else:
                            self.current_alerts.swing_bullish_bos = True
                    pivot_obj.crossed = True
                    trend_obj.bias = self.BULLISH
                    self.structure_breaks.append({
                        'type': tag,
                        'direction': 'bullish',
                        'internal': internal,
                        'price': pivot_obj.current_level,
                        'time': pivot_obj.bar_time,
                        'bar_index': pivot_obj.bar_index,
                        'break_time': self.times[current_bar],
                        'break_bar_index': current_bar,
                    })
                    self.store_order_block_bar(pivot_obj, internal, self.BULLISH, current_bar)
        pivot_obj = self.internal_low if internal else self.swing_low
        extra_condition = True
        if internal:
            extra_condition = (self.internal_low.current_level != self.swing_low.current_level and self._bearish_bar)
        if (pivot_obj.current_level is not None and
            current_close < pivot_obj.current_level and
            not pivot_obj.crossed and
            extra_condition):
            if current_bar > 0:
                prev_close = self.df.iloc[current_bar - 1]['close']
                if prev_close >= pivot_obj.current_level:
                    tag = self.CHOCH if trend_obj.bias != self.BEARISH else self.BOS
                    # print(f"Bearish break at index {current_bar}, price {pivot_obj.current_level:.2f}, type {tag}, trend {trend_obj.bias}")
                    if internal:
                        if tag == self.CHOCH:
                            self.current_alerts.internal_bearish_choch = True
                        else:
                            self.current_alerts.internal_bearish_bos = True
                    else:
                        if tag == self.CHOCH:
                            self.current_alerts.swing_bearish_choch = True
                        else:
                            self.current_alerts.swing_bearish_bos = True
                    pivot_obj.crossed = True
                    trend_obj.bias = self.BEARISH
                    self.structure_breaks.append({
                        'type': tag,
                        'direction': 'bearish',
                        'internal': internal,
                        'price': pivot_obj.current_level,
                        'time': pivot_obj.bar_time,
                        'bar_index': pivot_obj.bar_index,
                        'break_time': self.times[current_bar],
                        'break_bar_index': current_bar,
                    })
                    self.store_order_block_bar(pivot_obj, internal, self.BEARISH, current_bar)

    def store_order_block_bar(self, pivot_obj: Pivot, internal: bool, bias: int, current_bar: int):
        if ((not internal and self.show_swing_order_blocks_input) or
            (internal and self.show_internal_order_blocks_input)):
            if pivot_obj.bar_index is not None and pivot_obj.bar_index >= 0:
                start_idx = pivot_obj.bar_index
                end_idx = current_bar
                if start_idx < end_idx and end_idx < len(self.parsed_highs):
                    if bias == self.BEARISH:
                        array_slice = self.parsed_highs[start_idx:end_idx]
                        max_idx = np.argmax(array_slice)
                        parsed_index = start_idx + max_idx
                    else:
                        array_slice = self.parsed_lows[start_idx:end_idx]
                        min_idx = np.argmin(array_slice)
                        parsed_index = start_idx + min_idx
                    order_block = OrderBlock(
                        bar_high=self.parsed_highs[parsed_index],
                        bar_low=self.parsed_lows[parsed_index],
                        bar_time=self.times[parsed_index],
                        bias=bias
                    )
                    order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
                    if len(order_blocks) >= 100:
                        order_blocks.pop()
                    order_blocks.insert(0, order_block)

    def delete_order_blocks_bar(self, internal: bool, current_bar: int):
        order_blocks = self.internal_order_blocks if internal else self.swing_order_blocks
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_close = self.df.iloc[current_bar]['close']
        bearish_mitigation_source = current_close if self.order_block_mitigation_input == self.CLOSE else current_high
        bullish_mitigation_source = current_close if self.order_block_mitigation_input == self.CLOSE else current_low
        blocks_to_remove = []
        for i, order_block in enumerate(order_blocks):
            crossed_order_block = False
            if order_block.bias == self.BEARISH:
                if bearish_mitigation_source > order_block.bar_high:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bearish_order_block = True
                    else:
                        self.current_alerts.swing_bearish_order_block = True
            elif order_block.bias == self.BULLISH:
                if bullish_mitigation_source < order_block.bar_low:
                    crossed_order_block = True
                    if internal:
                        self.current_alerts.internal_bullish_order_block = True
                    else:
                        self.current_alerts.swing_bullish_order_block = True
            if crossed_order_block:
                blocks_to_remove.append(i)
        for i in reversed(blocks_to_remove):
            order_blocks.pop(i)

    def update_trailing_extremes_bar(self, current_bar: int):
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_time = self.times[current_bar]
        if self.trailing.top is None or current_high > self.trailing.top:
            self.trailing.top = current_high
            self.trailing.last_top_time = current_time
        if self.trailing.bottom is None or current_low < self.trailing.bottom:
            self.trailing.bottom = current_low
            self.trailing.last_bottom_time = current_time

    def calculate_premium_discount_zones_bar(self, current_bar: int):
        if self.trailing.top is not None and self.trailing.bottom is not None:
            premium_top = self.trailing.top
            premium_bottom = 0.95 * self.trailing.top + 0.05 * self.trailing.bottom
            equilibrium_top = 0.525 * self.trailing.top + 0.475 * self.trailing.bottom
            equilibrium_bottom = 0.525 * self.trailing.bottom + 0.475 * self.trailing.top
            discount_top = 0.95 * self.trailing.bottom + 0.05 * self.trailing.top
            discount_bottom = self.trailing.bottom
            self.premium_discount_zones = {
                'premium': {'top': premium_top, 'bottom': premium_bottom},
                'equilibrium': {'top': equilibrium_top, 'bottom': equilibrium_bottom},
                'discount': {'top': discount_top, 'bottom': discount_bottom}
            }

    def delete_fair_value_gaps_bar(self, current_bar: int):
        if not self.show_fair_value_gaps_input:
            return
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        fvgs_to_remove = []
        for i, fvg in enumerate(self.fair_value_gaps):
            if ((current_low < fvg.bottom and fvg.bias == self.BULLISH) or
                (current_high > fvg.top and fvg.bias == self.BEARISH)):
                # print(f"Removing FVG at bar {current_bar}: Bias={'Bullish' if fvg.bias == self.BULLISH else 'Bearish'}, Top={fvg.top:.2f}, Bottom={fvg.bottom:.2f}")
                fvgs_to_remove.append(i)
        for i in reversed(fvgs_to_remove):
            self.fair_value_gaps.pop(i)

    def detect_fair_value_gaps_bar(self, current_bar: int):
        if not self.show_fair_value_gaps_input or current_bar < 2:
            return
        current_high = self.highs[current_bar]
        current_low = self.lows[current_bar]
        current_time = self.times[current_bar]
        last_close = self.df.iloc[current_bar-1]['close']
        last_open = self.df.iloc[current_bar-1]['open']
        last_time = self.times[current_bar-1]
        last2_high = self.highs[current_bar-2]
        last2_low = self.lows[current_bar-2]
        bar_delta_percent = (last_close - last_open) / last_open if last_open != 0 else 0
        threshold = 0.002  # Fixed threshold of 0.2% for testing
        
        # print(f"Bar {current_bar}:")
        # print(f"  Current Low: {current_low:.2f}, Last2 High: {last2_high:.2f}, Last Close: {last_close:.2f}")
        # print(f"  Current High: {current_high:.2f}, Last2 Low: {last2_low:.2f}")
        # print(f"  Bar Delta %: {bar_delta_percent:.4f}, Threshold: {threshold:.4f}")
        # print(f"  Bullish FVG Conditions: current_low({current_low:.2f}) > last2_high({last2_high:.2f}), last_close({last_close:.2f}) > last2_high({last2_high:.2f}), bar_delta_percent({bar_delta_percent:.4f}) > threshold({threshold:.4f})")
        # print(f"  Bearish FVG Conditions: current_high({current_high:.2f}) < last2_low({last2_low:.2f}), last_close({last_close:.2f}) < last2_low({last2_low:.2f}), -bar_delta_percent({-bar_delta_percent:.4f}) > threshold({threshold:.4f})")
        
        bullish_fvg = (current_low > last2_high and last_close > last2_high and bar_delta_percent > threshold)
        bearish_fvg = (current_high < last2_low and last_close < last2_low and -bar_delta_percent > threshold)
        
        if bullish_fvg:
            # print(f"Bullish FVG detected at bar {current_bar}: Top={current_low:.2f}, Bottom={last2_high:.2f}")
            self.current_alerts.bullish_fair_value_gap = True
            fvg = FairValueGap(
                top=current_low,
                bottom=last2_high,
                bias=self.BULLISH,
                start_time=last_time,
                end_time=current_time + self.fair_value_gaps_extend_input,
                start_idx=current_bar - 1,
                width=self.fair_value_gaps_extend_input + 1
            )
            self.fair_value_gaps.insert(0, fvg)
        elif bearish_fvg:
            # print(f"Bearish FVG detected at bar {current_bar}: Top={current_high:.2f}, Bottom={last2_low:.2f}")
            self.current_alerts.bearish_fair_value_gap = True
            fvg = FairValueGap(
                top=current_high,
                bottom=last2_low,
                bias=self.BEARISH,
                start_time=last_time,
                end_time=current_time + self.fair_value_gaps_extend_input,
                start_idx=current_bar - 1,
                width=self.fair_value_gaps_extend_input + 1
            )
            self.fair_value_gaps.insert(0, fvg)

    def draw_equal_high_low_bar(self, pivot_obj: Pivot, level: float, size: int, equal_high: bool, current_bar: int):
        equal_data = {
            'type': 'EQH' if equal_high else 'EQL',
            'start_time': pivot_obj.bar_time,
            'start_level': pivot_obj.current_level,
            'end_time': self.times[current_bar],
            'end_level': level,
            'color': self.swing_bearish_color if equal_high else self.swing_bullish_color
        }
        if not hasattr(self, 'equal_structures'):
            self.equal_structures = []
        self.equal_structures.append(equal_data)
        if equal_high:
            self.current_alerts.equal_highs = True
        else:
            self.current_alerts.equal_lows = True

    def draw_order_blocks_final(self, internal: bool):
        pass

    async def run_analysis(self):
        if not await self.fetch_ohlcv():
            return False
        self.prepare_data()
        self.run_smc_analysis()
        print("Smart Money Concepts analysis completed")
        return True

    def plot_candlestick_chart(self, ax, start_idx: int = 0, end_idx: int = None):
        if end_idx is None:
            end_idx = len(self.df)
        df_slice = self.df.iloc[start_idx:end_idx]
        for i, (idx, row) in enumerate(df_slice.iterrows()):
            color = self.swing_bullish_color if row['close'] > row['open'] else self.swing_bearish_color
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['close'], row['open'])
            ax.add_patch(patches.Rectangle(
                (i, body_bottom), 0.8, body_height,
                facecolor=color, edgecolor='black', linewidth=0.5
            ))
            ax.plot([i+0.4, i+0.4], [row['low'], row['high']],
                    color='black', linewidth=0.5)

    def plot_structure_breaks(self, ax, start_idx: int = 0, end_idx: int = None):
        if not hasattr(self, 'structure_breaks') or not self.structure_breaks:
            return
        if end_idx is None:
            end_idx = len(self.df)
        for structure in self.structure_breaks:
            pivot_time = structure['time']
            time_diff = np.abs(self.times - pivot_time)
            pivot_time_idx = np.argmin(time_diff)
            plot_start_idx = pivot_time_idx - start_idx
            if plot_start_idx < -50:
                continue
            if structure['internal']:
                color = self.internal_bull_color_input if structure['direction'] == 'bullish' else self.internal_bear_color_input
            else:
                color = self.swing_bull_color_input if structure['direction'] == 'bullish' else self.swing_bear_color_input
            line_style = '--' if structure['internal'] else '-'
            detection_time = structure.get('break_time', pivot_time)
            detection_time_diff = np.abs(self.times - detection_time)
            detection_time_idx = np.argmin(detection_time_diff)
            plot_end_idx = detection_time_idx - start_idx
            actual_start = max(0, plot_start_idx)
            actual_end = min(end_idx - start_idx, plot_end_idx)
            if actual_start < actual_end:
                ax.plot([actual_start, actual_end],
                        [structure['price'], structure['price']],
                        color=color, linestyle=line_style, alpha=0.8, linewidth=1.5)
                label_x = (actual_start + actual_end) / 2  # Centered label
                label_y_offset = (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.005
                if structure['direction'] == 'bullish':
                    label_y = structure['price'] + label_y_offset
                    va = 'bottom'
                else:
                    label_y = structure['price'] - label_y_offset
                    va = 'top'
                ax.text(label_x, label_y, structure['type'],
                        color=color, fontsize=9, ha='center', va=va, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3))

        # Center the plot by adjusting x-axis limits
        all_start_indices = [max(0, pivot_time_idx - start_idx) for structure in self.structure_breaks 
                            if (pivot_time_idx - start_idx) >= -50 and (detection_time_idx - start_idx) < end_idx]
        all_end_indices = [min(end_idx - start_idx, detection_time_idx - start_idx) for structure in self.structure_breaks 
                        if (pivot_time_idx - start_idx) >= -50 and (detection_time_idx - start_idx) < end_idx]
        if all_start_indices and all_end_indices:
            min_x = min(all_start_indices)
            max_x = max(all_end_indices)
            x_range = max_x - min_x
            ax.set_xlim(min_x - x_range * 0.1, max_x + x_range * 0.1)  # Add 10% padding on both sides

    def plot_order_blocks(self, ax, start_idx: int = 0, end_idx: int = None):
        if end_idx is None:
            end_idx = len(self.df)
        for i, ob in enumerate(self.swing_order_blocks):
            if i >= self.swing_order_blocks_size_input:
                break
            time_idx = np.where(self.times == ob.bar_time)[0]
            if len(time_idx) > 0:
                time_idx = time_idx[0]
                plot_start_idx = time_idx - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    color = self.swing_bullish_order_block_color if ob.bias == self.BULLISH else self.swing_bearish_order_block_color
                    actual_start = max(0, plot_start_idx)
                    width = (end_idx - start_idx) - actual_start
                    height = ob.bar_high - ob.bar_low
                    if width > 0:
                        ax.add_patch(patches.Rectangle(
                            (actual_start, ob.bar_low), width, height,
                            facecolor=color, edgecolor=color,
                            alpha=0.3, linewidth=1
                        ))
        for i, ob in enumerate(self.internal_order_blocks):
            if i >= self.internal_order_blocks_size_input:
                break
            time_idx = np.where(self.times == ob.bar_time)[0]
            if len(time_idx) > 0:
                time_idx = time_idx[0]
                plot_start_idx = time_idx - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    color = self.internal_bullish_order_block_color if ob.bias == self.BULLISH else self.internal_bearish_order_block_color
                    actual_start = max(0, plot_start_idx)
                    width = (end_idx - start_idx) - actual_start
                    height = ob.bar_high - ob.bar_low
                    if width > 0:
                        ax.add_patch(patches.Rectangle(
                            (actual_start, ob.bar_low), width, height,
                            facecolor=color, edgecolor=color,
                            alpha=0.3, linewidth=1
                        ))

    def plot_equal_highs_lows(self, ax, start_idx: int = 0, end_idx: int = None):
        if not hasattr(self, 'equal_structures'):
            return
        if end_idx is None:
            end_idx = len(self.df)
        for equal in self.equal_structures:
            start_time_idx = np.where(self.times == equal['start_time'])[0]
            end_time_idx = np.where(self.times == equal['end_time'])[0]
            if len(start_time_idx) > 0 and len(end_time_idx) > 0:
                start_plot_idx = start_time_idx[0] - start_idx
                end_plot_idx = end_time_idx[0] - start_idx
                if start_plot_idx < end_idx - start_idx and end_plot_idx > 0:
                    actual_start = max(0, start_plot_idx)
                    actual_end = min(end_idx - start_idx, end_plot_idx)
                    ax.plot([actual_start, actual_end],
                            [equal['start_level'], equal['end_level']],
                            color=equal['color'], linewidth=1.5, linestyle=':', alpha=0.8)
                    mid_x = (actual_start + actual_end) / 2
                    mid_y = (equal['start_level'] + equal['end_level']) / 2
                    ax.text(mid_x, mid_y,
                            equal['type'], color=equal['color'],
                            fontsize=8, ha='center', va='center', weight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor=equal['color'], alpha=0.3))

    def plot_fair_value_gaps(self, ax, start_idx: int = 0, end_idx: int = None):
        if not self.show_fair_value_gaps_input or not hasattr(self, 'fair_value_gaps'):
            return
        if end_idx is None:
            end_idx = len(self.df)
        for fvg in self.fair_value_gaps:
            if hasattr(fvg, 'start_idx') and fvg.start_idx is not None:
                plot_start_idx = fvg.start_idx - start_idx
                plot_width = fvg.width
            else:
                plot_start_idx = 0
                plot_width = 10
            if plot_start_idx <= end_idx - start_idx and plot_start_idx + plot_width >= 0:
                actual_start = max(0, plot_start_idx)
                actual_width = min(plot_width, end_idx - start_idx - actual_start)
                if actual_width > 0:
                    color = self.fair_value_gap_bullish_color if fvg.bias == self.BULLISH else self.fair_value_gap_bearish_color
                    height = fvg.top - fvg.bottom
                    ax.add_patch(patches.Rectangle(
                        (actual_start, fvg.bottom), actual_width, height,
                        facecolor=color, edgecolor=color,
                        alpha=0.3, linewidth=1
                    ))
                    label_text = 'FVG' if fvg.bias == self.BULLISH else 'FVG'
                    mid_x = actual_start + actual_width / 2
                    mid_y = (fvg.top + fvg.bottom) / 2
                    ax.text(mid_x, mid_y, label_text,
                            color=color[:-2] if len(color) > 7 else color,
                            fontsize=6, ha='center', va='center', weight='bold',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor=color, alpha=0.5))

    def plot_premium_discount_zones(self, ax, start_idx: int = 0, end_idx: int = None):
        if not self.show_premium_discount_zones_input or not hasattr(self, 'premium_discount_zones'):
            return
        if end_idx is None:
            end_idx = len(self.df)
        zone_colors = {
            'premium': self.premium_zone_color,
            'equilibrium': self.equilibrium_zone_color_input,
            'discount': self.discount_zone_color
        }
        for zone_name, zone_data in self.premium_discount_zones.items():
            base_color = zone_colors.get(zone_name, '#808080')
            ax.axhspan(zone_data['bottom'], zone_data['top'],
                       facecolor=base_color, alpha=0.15, zorder=1)
            mid_price = (zone_data['top'] + zone_data['bottom']) / 2
            ax.text(end_idx - start_idx - 5, mid_price, zone_name.capitalize(),
                    color=base_color, fontsize=10, ha='right', va='center',
                    weight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=base_color, alpha=0.3))

    def plot_trailing_extremes(self, ax, start_idx: int = 0, end_idx: int = None):
        if not self.show_high_low_swings_input:
            return
        if end_idx is None:
            end_idx = len(self.df)
        bars_to_extend = 20
        right_time_bar = end_idx - start_idx + bars_to_extend
        if hasattr(self.trailing, 'last_top_time') and self.trailing.last_top_time is not None:
            top_time_idx = np.where(self.times == self.trailing.last_top_time)[0]
            if len(top_time_idx) > 0:
                plot_start_idx = top_time_idx[0] - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    actual_start = max(0, plot_start_idx)
                    actual_end = min(right_time_bar, end_idx - start_idx)
                    ax.plot([actual_start, actual_end],
                            [self.trailing.top, self.trailing.top],
                            color=self.swing_bearish_color, linewidth=2, linestyle='-', alpha=0.8)
                    trend_label = 'Strong High' if self.swing_trend.bias == self.BEARISH else 'Weak High'
                    ax.text(actual_end - 2, self.trailing.top, trend_label,
                            color=self.swing_bearish_color, fontsize=9,
                            ha='right', va='bottom', weight='bold')
        if hasattr(self.trailing, 'last_bottom_time') and self.trailing.last_bottom_time is not None:
            bottom_time_idx = np.where(self.times == self.trailing.last_bottom_time)[0]
            if len(bottom_time_idx) > 0:
                plot_start_idx = bottom_time_idx[0] - start_idx
                if plot_start_idx <= end_idx - start_idx:
                    actual_start = max(0, plot_start_idx)
                    actual_end = min(right_time_bar, end_idx - start_idx)
                    ax.plot([actual_start, actual_end],
                            [self.trailing.bottom, self.trailing.bottom],
                            color=self.swing_bullish_color, linewidth=2, linestyle='-', alpha=0.8)
                    trend_label = 'Strong Low' if self.swing_trend.bias == self.BULLISH else 'Weak Low'
                    ax.text(actual_end - 2, self.trailing.bottom, trend_label,
                            color=self.swing_bullish_color, fontsize=9,
                            ha='right', va='top', weight='bold')

    def visualize_smc(self, bars_to_show: int = 1000):
        if self.df is None:
            print("No data available for visualization")
            return
        total_bars = len(self.df)
        start_idx = max(0, total_bars - bars_to_show)
        end_idx = total_bars
        fig, ax = plt.subplots(figsize=(15, 10))
        self.plot_candlestick_chart(ax, start_idx, end_idx)
        self.plot_premium_discount_zones(ax, start_idx, end_idx)
        self.plot_fair_value_gaps(ax, start_idx, end_idx)
        self.plot_order_blocks(ax, start_idx, end_idx)
        self.plot_structure_breaks(ax, start_idx, end_idx)
        self.plot_equal_highs_lows(ax, start_idx, end_idx)
        self.plot_trailing_extremes(ax, start_idx, end_idx)
        ax.set_xlim(0, bars_to_show)
        ax.set_ylim(self.df.iloc[start_idx:end_idx]['low'].min() * 0.995,
                    self.df.iloc[start_idx:end_idx]['high'].max() * 1.005)
        ax.set_title(f"{self.stock_code} - Smart Money Concepts",
                     fontsize=16, fontweight='bold')
        ax.set_xlabel("Bars", fontsize=12)
        ax.set_ylabel("Price", fontsize=12)
        ax.grid(True, alpha=0.3)
        legend_elements = [
            plt.Line2D([0], [0], color=self.swing_bullish_color, lw=2, label='Bullish Structure'),
            plt.Line2D([0], [0], color=self.swing_bearish_color, lw=2, label='Bearish Structure'),
            patches.Patch(color=self.swing_bullish_order_block_color, alpha=0.3, label='Swing Order Blocks'),
            patches.Patch(color=self.internal_bullish_order_block_color, alpha=0.3, label='Internal Order Blocks')
        ]
        if self.show_equal_highs_lows_input:
            legend_elements.append(plt.Line2D([0], [0], color=self.swing_bullish_color,
                                              lw=1, linestyle=':', label='Equal Highs/Lows'))
        if self.show_fair_value_gaps_input:
            legend_elements.append(patches.Patch(color=self.fair_value_gap_bullish_color,
                                                alpha=0.2, label='Fair Value Gaps'))
        if self.show_premium_discount_zones_input:
            legend_elements.append(patches.Patch(color=self.premium_zone_color,
                                                alpha=0.1, label='Premium/Discount Zones'))
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.show()
        self.print_analysis_summary()

    # In print_analysis_summary method
    def print_analysis_summary(self):
        print("\n" + "="*80)
        print("\nSMART MONEY CONCEPTS ANALYSIS SUMMARY")
        print("\n" + "="*80)
        print(f"Stock Code: {self.stock_code}")
        print(f"Total Bars Analyzed: {len(self.df)}")
        print(f"Data Range: {self.df.index[0]} to {self.df.index[-1]}")
        print("-" * 80)
        print("\nSTRUCTURE ANALYSIS:")
        if hasattr(self, 'structure_breaks'):
            ## Log structure_breaks for debugging
            # print("Structure Breaks Detected:")
            # for s in self.structure_breaks:
            #     print(f"Type: {s['type']}, Direction: {s['direction']}, Internal: {s['internal']}, Price: {s['price']:.2f}, Time: {s['time']}")
            swing_bos = len([s for s in self.structure_breaks if s['type'] == self.BOS and not s['internal']])
            swing_choch = len([s for s in self.structure_breaks if s['type'] == self.CHOCH and not s['internal']])
            internal_bos = len([s for s in self.structure_breaks if s['type'] == self.BOS and s['internal']])
            internal_choch = len([s for s in self.structure_breaks if s['type'] == self.CHOCH and s['internal']])
            print(f"Swing BOS: {swing_bos}")
            print(f"Swing CHoCH: {swing_choch}")
            print(f"Internal BOS: {internal_bos}")
            print(f"Internal CHoCH: {internal_choch}")
        else:
            print("No structure breaks found.")
        print("\nCURRENT TREND:")
        swing_trend = "Bullish" if self.swing_trend.bias == self.BULLISH else "Bearish" if self.swing_trend.bias == self.BEARISH else "Neutral"
        internal_trend = "Bullish" if self.internal_trend.bias == self.BULLISH else "Bearish" if self.internal_trend.bias == self.BEARISH else "Neutral"
        print(f"Swing Trend: {swing_trend}")
        print(f"Internal Trend: {internal_trend}")
        print("\nORDER BLOCKS:")
        print(f"Swing Order Blocks: {len(self.swing_order_blocks)}")
        print(f"Internal Order Blocks: {len(self.internal_order_blocks)}")
        if hasattr(self, 'equal_structures'):
            eqh_count = len([e for e in self.equal_structures if e['type'] == 'EQH'])
            eql_count = len([e for e in self.equal_structures if e['type'] == 'EQL'])
            print("\nEQUAL HIGHS/LOWS:")
            print(f"Equal Highs (EQH): {eqh_count}")
            print(f"Equal Lows (EQL): {eql_count}")
        if self.show_fair_value_gaps_input:
            bullish_fvg = len([f for f in self.fair_value_gaps if f.bias == self.BULLISH])
            bearish_fvg = len([f for f in self.fair_value_gaps if f.bias == self.BEARISH])
            print("\nFAIR VALUE GAPS:")
            print(f"Bullish FVG: {bullish_fvg}")
            print(f"Bearish FVG: {bearish_fvg}")
        print("\nTRAILING EXTREMES:")
        if self.trailing.top is not None:
            print(f"Trailing High: {self.trailing.top:.2f}")
        if self.trailing.bottom is not None:
            print(f"Trailing Low: {self.trailing.bottom:.2f}")
        if self.show_premium_discount_zones_input and hasattr(self, 'premium_discount_zones'):
            print("\nPREMIUM/DISCOUNT ZONES:")
            for zone_name, zone_data in self.premium_discount_zones.items():
                print(f"{zone_name.capitalize()}: Bottom = {zone_data['bottom']:.2f}, Top = {zone_data['top']:.2f}")
        current_price = self.df.iloc[-1]['close']
        print("\nPRICE ANALYSIS:")
        print(f"Current Price: {current_price:.2f}")
        if self.show_premium_discount_zones_input and hasattr(self, 'premium_discount_zones'):
            if current_price >= self.premium_discount_zones['premium']['bottom']:
                current_zone = "Premium"
            elif current_price <= self.premium_discount_zones['discount']['top']:
                current_zone = "Discount"
            else:
                current_zone = "Equilibrium"
            print(f"Current Zone: {current_zone}")
        print("=" * 80)
        print("Analysis completed successfully!")
        print("=" * 80 + "\n")
