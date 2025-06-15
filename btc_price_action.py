#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTC Price Action Analysis - Based on Al Brooks Theory
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import os
import ccxt
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

def get_btc_data(period='6mo', interval='1d'):
    """Fetch BTC data"""
    try:
        print("Fetching BTC data...")
        data = yf.download('BTC-USD', period=period, interval=interval, progress=False)
        
        if data.empty:
            return None
            
        # Fix multi-level column index issue
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        print(f"✅ Successfully fetched {len(data)} rows of data")
        return data
        
    except Exception as e:
        print(f"❌ Failed to fetch data: {e}")
        return None

def calculate_price_action(data):
    """Calculate price action indicators"""
    try:
        # Calculate candlestick body and shadows
        data['Body'] = data['Close'] - data['Open']
        data['Upper_Shadow'] = data['High'] - data[['Open', 'Close']].max(axis=1)
        data['Lower_Shadow'] = data[['Open', 'Close']].min(axis=1) - data['Low']
        data['Total_Length'] = data['High'] - data['Low']
        
        # Calculate body and shadow ratios
        data['Body_Ratio'] = abs(data['Body']) / data['Total_Length']
        data['Upper_Shadow_Ratio'] = data['Upper_Shadow'] / data['Total_Length']
        data['Lower_Shadow_Ratio'] = data['Lower_Shadow'] / data['Total_Length']
        
        # Trend determination
        data['Trend'] = np.where(data['Close'] > data['Open'], 'Bull', 'Bear')
        
        # Trend strength
        data['Trend_Strength'] = np.where(
            data['Body_Ratio'] > 0.6, 'Strong',
            np.where(data['Body_Ratio'] > 0.4, 'Moderate', 'Weak')
        )
        
        # Support and resistance
        lookback = 20
        data['Resistance'] = data['High'].rolling(window=lookback).max()
        data['Support'] = data['Low'].rolling(window=lookback).min()
        
        # Volatility (ATR)
        data['ATR'] = (data['High'] - data['Low']).rolling(window=14).mean()
        
        return data
        
    except Exception as e:
        print(f"Failed to calculate price action indicators: {e}")
        return None

def detect_patterns(data):
    """Detect Al Brooks patterns"""
    try:
        patterns = []
        
        for i in range(2, len(data)):
            # Engulfing pattern
            if (data['Body'].iloc[i] > 0 and data['Body'].iloc[i-1] < 0 and
                abs(data['Body'].iloc[i]) > abs(data['Body'].iloc[i-1]) * 1.1):
                patterns.append(('Bullish_Engulfing', i))
            elif (data['Body'].iloc[i] < 0 and data['Body'].iloc[i-1] > 0 and
                  abs(data['Body'].iloc[i]) > abs(data['Body'].iloc[i-1]) * 1.1):
                patterns.append(('Bearish_Engulfing', i))
            
            # Inside bar
            if (data['High'].iloc[i] < data['High'].iloc[i-1] and
                data['Low'].iloc[i] > data['Low'].iloc[i-1]):
                patterns.append(('Inside_Bar', i))
            
            # Outside bar
            if (data['High'].iloc[i] > data['High'].iloc[i-1] and
                data['Low'].iloc[i] < data['Low'].iloc[i-1]):
                patterns.append(('Outside_Bar', i))
            
            # Three pushes pattern
            if i >= 4:
                highs = [data['High'].iloc[i-j] for j in range(4)]
                lows = [data['Low'].iloc[i-j] for j in range(4)]
                
                if (highs[0] > highs[1] > highs[2] > highs[3] and
                    data['Trend'].iloc[i] == 'Bear'):
                    patterns.append(('Three_Pushes_Down', i))
                elif (lows[0] < lows[1] < lows[2] < lows[3] and
                      data['Trend'].iloc[i] == 'Bull'):
                    patterns.append(('Three_Pushes_Up', i))
        
        return patterns
        
    except Exception as e:
        print(f"Failed to detect patterns: {e}")
        return []

def generate_signals(data, patterns):
    """Generate trading signals"""
    try:
        signals = []
        
        for i in range(len(data)):
            if i < 20:  # Not enough data
                signals.append('Hold')
                continue
                
            current_price = data['Close'].iloc[i]
            trend = data['Trend'].iloc[i]
            strength = data['Trend_Strength'].iloc[i]
            resistance = data['Resistance'].iloc[i-1]
            support = data['Support'].iloc[i-1]
            
            # Check if current candle has a pattern
            current_patterns = [p for p in patterns if p[1] == i]
            
            # Generate signal
            if current_patterns:
                pattern_name = current_patterns[0][0]
                
                if pattern_name == 'Bullish_Engulfing':
                    signals.append('Strong_Buy')
                elif pattern_name == 'Bearish_Engulfing':
                    signals.append('Strong_Sell')
                elif pattern_name == 'Inside_Bar':
                    signals.append('Wait')
                elif pattern_name == 'Outside_Bar':
                    if trend == 'Bull':
                        signals.append('Buy')
                    else:
                        signals.append('Sell')
                elif pattern_name == 'Three_Pushes_Down':
                    signals.append('Sell')
                elif pattern_name == 'Three_Pushes_Up':
                    signals.append('Buy')
            else:
                # Signal based on trend and support/resistance
                if trend == 'Bull' and strength == 'Strong' and current_price > resistance:
                    signals.append('Buy')
                elif trend == 'Bear' and strength == 'Strong' and current_price < support:
                    signals.append('Sell')
                elif trend == 'Bull' and current_price < support:
                    signals.append('Buy_Dip')
                elif trend == 'Bear' and current_price > resistance:
                    signals.append('Sell_Rally')
                else:
                    signals.append('Hold')
        
        data['Signal'] = signals
        return data
        
    except Exception as e:
        print(f"Failed to generate signals: {e}")
        return None

def plot_analysis(data, patterns):
    """Plot analysis chart"""
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Price chart
        ax1.plot(data.index, data['Close'], label='BTC Price', linewidth=2)
        
        # Support and resistance
        ax1.plot(data.index, data['Resistance'], 'r--', alpha=0.5, label='Resistance')
        ax1.plot(data.index, data['Support'], 'g--', alpha=0.5, label='Support')
        
        # Buy/sell signals
        buy_signals = data[data['Signal'].isin(['Buy', 'Strong_Buy', 'Buy_Dip'])]
        sell_signals = data[data['Signal'].isin(['Sell', 'Strong_Sell', 'Sell_Rally'])]
        
        if not buy_signals.empty:
            ax1.scatter(buy_signals.index, buy_signals['Close'], 
                       marker='^', color='green', s=100, alpha=0.8, label='Buy')
        if not sell_signals.empty:
            ax1.scatter(sell_signals.index, sell_signals['Close'], 
                       marker='v', color='red', s=100, alpha=0.8, label='Sell')
        
        # Mark patterns
        for pattern, idx in patterns:
            if pattern in ['Bullish_Engulfing', 'Bearish_Engulfing']:
                color = 'green' if pattern == 'Bullish_Engulfing' else 'red'
                ax1.scatter(data.index[idx], data['Close'].iloc[idx], 
                           marker='*', color=color, s=200, alpha=0.8)
        
        ax1.set_title('BTC Price Action Analysis')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volatility chart
        ax2.plot(data.index, data['ATR'], color='purple', label='ATR')
        ax2.set_ylabel('Volatility')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Failed to plot: {e}")

def print_recent_signals(data, days=5):
    """Print recent signals"""
    if data is None or len(data) < days:
        return
        
    recent = data.tail(days)
    
    print(f"\n📊 Last {days} days BTC analysis:")
    print("-" * 60)
    
    for date, row in recent.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        price = row['Close']
        signal = row['Signal']
        trend = row['Trend']
        strength = row['Trend_Strength']
        
        emoji = "📈" if trend == 'Bull' else "📉"
        
        if signal != 'Hold':
            print(f"{date_str} {emoji} Price: ${price:8.2f} Trend: {trend} Strength: {strength} Signal: {signal}")

def get_btc_okx_4h_data(limit=200):
    """Fetch BTC/USDT 4h data from OKX API using env credentials"""
    load_dotenv()
    api_key = os.getenv("OKX_API_KEY")
    api_secret = os.getenv("OKX_API_SECRET")
    passphrase = os.getenv("OKX_PASSPHRASE")
    if not all([api_key, api_secret, passphrase]):
        print("❌ OKX API credentials not set in environment variables.")
        return None
    exchange = ccxt.okx({
        'apiKey': api_key,
        'secret': api_secret,
        'password': passphrase,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot',
            'adjustForTimeDifference': True
        }
    })
    try:
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='4h', limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"❌ Failed to fetch BTC/USDT 4h data from OKX: {e}")
        return None

def main():
    """Main function"""
    print("🏆 BTC Price Action Analysis - Al Brooks Style")
    print("=" * 50)
    # Try OKX 4h data first
    data = get_btc_okx_4h_data(limit=200)
    if data is not None:
        print("Using BTC/USDT 4h data from OKX API.")
        interval = '4h'
    else:
        print("Falling back to yfinance BTC-USD daily data.")
        data = get_btc_data(period='3mo', interval='1d')
        interval = '1d'
    if data is not None:
        data = calculate_price_action(data)
        if data is not None:
            patterns = detect_patterns(data)
            data = generate_signals(data, patterns)
            if data is not None:
                print_recent_signals(data, days=5)
                signal_counts = data['Signal'].value_counts()
                print(f"\nSignal statistics:")
                for signal, count in signal_counts.items():
                    if signal != 'Hold':
                        print(f"  {signal}: {count} times")
                # Show buy/sell table
                buy_sell_signals = ['Buy', 'Strong_Buy', 'Buy_Dip', 'Sell', 'Strong_Sell', 'Sell_Rally']
                df_signals = data[data['Signal'].isin(buy_sell_signals)].copy()
                if not df_signals.empty:
                    table = df_signals[['Close', 'Signal', 'Trend', 'Trend_Strength']].copy()
                    table.index.name = 'Time'
                    print("\nBuy/Sell Signals Table:")
                    print(table.tail(20).to_markdown())
                else:
                    print("\nNo buy/sell signals found.")
                plot_analysis(data, patterns)
                print(f"\n✅ Analysis completed!")
            else:
                print("❌ Failed to generate signals")
        else:
            print("❌ Failed to calculate price action indicators")
    else:
        print("❌ Failed to fetch data")

if __name__ == "__main__":
    main() 