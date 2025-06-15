#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黄金(XAU/USD)技术分析 - 简化版本
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import warnings
import time
warnings.filterwarnings('ignore')

def get_simple_data(ticker='GLD', period='6mo'):
    """获取简化的股票数据"""
    try:
        print(f"正在获取 {ticker} 数据...")
        data = yf.download(ticker, period=period, interval='1d', progress=False)
        
        if data.empty:
            return None
        
        # 修复多级列索引问题
        if isinstance(data.columns, pd.MultiIndex):
            # 如果是多级索引，取第一级
            data.columns = data.columns.droplevel(1)
        
        # 确保有必要的列
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in data.columns:
                print(f"缺少必要的列: {col}")
                return None
        
        # 只计算最基础的指标
        data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        
        # 手动计算RSI，避免对齐问题
        close_prices = data['Close'].values
        rsi_values = []
        
        for i in range(len(close_prices)):
            if i < 14:
                rsi_values.append(50.0)  # 默认值
            else:
                # 计算14天的价格变化
                gains = []
                losses = []
                for j in range(i-13, i+1):
                    change = close_prices[j] - close_prices[j-1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                
                avg_gain = sum(gains) / 14
                avg_loss = sum(losses) / 14
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                rsi_values.append(rsi)
        
        data['RSI'] = rsi_values
        
        # 趋势判断
        trend_list = []
        for i in range(len(data)):
            close_val = float(data['Close'].iloc[i])
            ema_val = data['EMA_20'].iloc[i]
            if pd.isna(ema_val):
                ema_val = close_val
            else:
                ema_val = float(ema_val)
            trend_list.append('Bull' if close_val > ema_val else 'Bear')
        
        data['Trend'] = trend_list
        
        # 简单信号
        signals = []
        for i in range(len(data)):
            if i < 20:  # 数据不足
                signals.append('Hold')
                continue
                
            current_price = data['Close'].iloc[i]
            ema = data['EMA_20'].iloc[i]
            rsi = data['RSI'].iloc[i]
            trend = data['Trend'].iloc[i]
            
            # 生成信号
            if trend == 'Bull' and current_price > ema * 1.005 and rsi < 70:
                signals.append('Buy')
            elif trend == 'Bear' and current_price < ema * 0.995 and rsi > 30:
                signals.append('Sell')
            elif rsi > 80:
                signals.append('Take Profit')
            elif rsi < 20:
                signals.append('Buy Dip')
            else:
                signals.append('Hold')
        
        data['Signal'] = signals
        
        print(f"✅ 成功获取 {len(data)} 条数据")
        return data
        
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return None

def print_recent_analysis(data, ticker, days=5):
    """打印最近的分析结果"""
    if data is None or len(data) < days:
        return
        
    recent = data.tail(days)
    
    print(f"\n📊 {ticker} 最近 {days} 天分析:")
    print("-" * 50)
    
    for date, row in recent.iterrows():
        date_str = date.strftime('%Y-%m-%d')
        price = row['Close']
        signal = row['Signal']
        rsi = row['RSI'] if not pd.isna(row['RSI']) else 50
        trend = row['Trend']
        
        emoji = "📈" if trend == 'Bull' else "📉"
        
        if signal != 'Hold':
            print(f"{date_str} {emoji} 价格:${price:6.2f} RSI:{rsi:5.1f} 信号:{signal}")

def simple_plot(data, ticker):
    """简单绘图"""
    if data is None or len(data) < 20:
        print("数据不足，无法绘图")
        return
        
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 价格图
        ax1.plot(data.index, data['Close'], label=f'{ticker} 价格', linewidth=2)
        ax1.plot(data.index, data['EMA_20'], label='20日EMA', linestyle='--', alpha=0.7)
        
        # 买卖信号
        buy_data = data[data['Signal'].isin(['Buy', 'Buy Dip'])]
        sell_data = data[data['Signal'].isin(['Sell', 'Take Profit'])]
        
        if not buy_data.empty:
            ax1.scatter(buy_data.index, buy_data['Close'], 
                       marker='^', color='green', s=50, alpha=0.8, label='买入')
        if not sell_data.empty:
            ax1.scatter(sell_data.index, sell_data['Close'], 
                       marker='v', color='red', s=50, alpha=0.8, label='卖出')
        
        ax1.set_title(f'{ticker} 价格走势与交易信号')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # RSI图
        if 'RSI' in data.columns:
            ax2.plot(data.index, data['RSI'], color='purple', label='RSI')
            ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax2.set_ylabel('RSI')
            ax2.set_ylim(0, 100)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"绘图失败: {e}")

def main():
    """主函数"""
    print("🏆 黄金技术分析 - 简化版")
    print("=" * 40)
    
    # 测试的标的
    tickers = {
        'GLD': 'SPDR黄金ETF',
        'IAU': 'iShares黄金ETF', 
        'AAPL': '苹果公司'  # 备用测试
    }
    
    success_count = 0
    
    for ticker, name in tickers.items():
        print(f"\n🔍 分析: {name} ({ticker})")
        
        data = get_simple_data(ticker, period='3mo')
        
        if data is not None:
            success_count += 1
            print_recent_analysis(data, ticker, days=5)
            
            # 统计信号
            signal_counts = data['Signal'].value_counts()
            print(f"\n信号统计:")
            for signal, count in signal_counts.items():
                if signal != 'Hold':
                    print(f"  {signal}: {count} 次")
            
            # 只为第一个成功的画图
            if success_count == 1:
                simple_plot(data, ticker)
            
            # 找到一个成功的就停止
            break
        else:
            print(f"跳过 {ticker}")
    
    if success_count == 0:
        print("\n⚠️  无法获取任何数据，请检查网络连接")
    else:
        print(f"\n✅ 分析完成!")

if __name__ == "__main__":
    main()
