import os
import requests
import hmac
import hashlib
import base64
import json
import time
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from dotenv import load_dotenv
import talib

# 加载环境变量
load_dotenv()

class OKXScanner:
    def __init__(self):
        self.api_key = os.getenv('OKX_API_KEY')
        self.api_secret = os.getenv('OKX_API_SECRET')
        self.passphrase = os.getenv('OKX_PASSPHRASE')
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        self.base_url = 'https://www.okx.com'
        
        # 时间级别映射
        self.timeframes = {
            '5m': '5m',
            '15m': '15m',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }
        
    def get_signature(self, timestamp, method, request_path, body=''):
        """生成API签名"""
        message = timestamp + method + request_path + body
        mac = hmac.new(
            bytes(self.api_secret, encoding='utf8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode()
    
    def get_headers(self, method, request_path, body=''):
        """获取API请求头"""
        timestamp = datetime.now(timezone.utc).isoformat()[:-3] + 'Z'
        signature = self.get_signature(timestamp, method, request_path, body)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_top_volume_pairs(self, limit=200):
        """获取24小时交易量前200的交易对"""
        url = f"{self.base_url}/api/v5/market/tickers?instType=SPOT"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == '0':
                tickers = data['data']
                # 按24小时交易量排序
                sorted_tickers = sorted(tickers, key=lambda x: float(x['vol24h']), reverse=True)
                return [ticker['instId'] for ticker in sorted_tickers[:limit]]
            else:
                print(f"获取交易对失败: {data['msg']}")
                return []
                
        except Exception as e:
            print(f"获取交易对时出错: {e}")
            return []
    
    def get_kline_data(self, symbol, timeframe, limit=100):
        """获取K线数据"""
        url = f"{self.base_url}/api/v5/market/candles"
        params = {
            'instId': symbol,
            'bar': timeframe,
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['code'] == '0':
                candles = data['data']
                # 转换为DataFrame
                df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm'])
                df = df.astype({
                    'open': float,
                    'high': float,
                    'low': float,
                    'close': float,
                    'volume': float
                })
                # OKX返回的数据是倒序的，需要正序
                df = df[::-1].reset_index(drop=True)
                return df
            else:
                print(f"获取K线数据失败 {symbol}: {data['msg']}")
                return None
                
        except Exception as e:
            print(f"获取K线数据时出错 {symbol}: {e}")
            return None
    
    def calculate_rsi(self, df, period=14):
        """计算RSI"""
        try:
            rsi = talib.RSI(df['close'].values, timeperiod=period)
            return rsi
        except Exception as e:
            print(f"计算RSI时出错: {e}")
            return None
    
    def is_pinbar_bearish(self, df, index, ratio=0.3):
        """检测看跌Pin Bar"""
        try:
            row = df.iloc[index]
            body = abs(row['close'] - row['open'])
            upper_shadow = row['high'] - max(row['close'], row['open'])
            lower_shadow = min(row['close'], row['open']) - row['low']
            total_range = row['high'] - row['low']
            
            if total_range == 0:
                return False
                
            return (upper_shadow > total_range * (1 - ratio) and 
                    body < total_range * ratio and 
                    lower_shadow < total_range * ratio)
        except:
            return False
    
    def is_pinbar_bullish(self, df, index, ratio=0.3):
        """检测看涨Pin Bar"""
        try:
            row = df.iloc[index]
            body = abs(row['close'] - row['open'])
            upper_shadow = row['high'] - max(row['close'], row['open'])
            lower_shadow = min(row['close'], row['open']) - row['low']
            total_range = row['high'] - row['low']
            
            if total_range == 0:
                return False
                
            return (lower_shadow > total_range * (1 - ratio) and 
                    body < total_range * ratio and 
                    upper_shadow < total_range * ratio)
        except:
            return False
    
    def is_bearish_engulfing(self, df, index):
        """检测看跌吞没"""
        try:
            if index < 1:
                return False
                
            prev = df.iloc[index - 1]
            curr = df.iloc[index]
            
            # 前一根K线为阳线，当前K线为阴线
            prev_bullish = prev['open'] < prev['close']
            curr_bearish = curr['open'] > curr['close']
            
            # 当前K线完全吞没前一根K线
            engulfing = curr['close'] < prev['open'] and curr['open'] > prev['close']
            
            return prev_bullish and curr_bearish and engulfing
        except:
            return False
    
    def is_bullish_engulfing(self, df, index):
        """检测看涨吞没"""
        try:
            if index < 1:
                return False
                
            prev = df.iloc[index - 1]
            curr = df.iloc[index]
            
            # 前一根K线为阴线，当前K线为阳线
            prev_bearish = prev['open'] > prev['close']
            curr_bullish = curr['open'] < curr['close']
            
            # 当前K线完全吞没前一根K线
            engulfing = curr['close'] > prev['open'] and curr['open'] < prev['close']
            
            return prev_bearish and curr_bullish and engulfing
        except:
            return False
    
    def analyze_symbol(self, symbol, timeframe):
        """分析单个交易对"""
        df = self.get_kline_data(symbol, timeframe)
        if df is None or len(df) < 20:
            return None
            
        # 计算RSI
        rsi = self.calculate_rsi(df)
        if rsi is None:
            return None
            
        current_rsi = rsi[-1]
        last_index = len(df) - 1
        
        # 检测信号
        signals = []
        
        # 看跌信号: RSI > 70 + (Pin Bar 或 吞没)
        if current_rsi > 70:
            if self.is_pinbar_bearish(df, last_index):
                signals.append({
                    'type': '做空',
                    'reason': 'RSI超买 + 看跌Pin Bar',
                    'rsi': current_rsi,
                    'price': df.iloc[last_index]['close']
                })
            elif self.is_bearish_engulfing(df, last_index):
                signals.append({
                    'type': '做空',
                    'reason': 'RSI超买 + 看跌吞没',
                    'rsi': current_rsi,
                    'price': df.iloc[last_index]['close']
                })
        
        # 看涨信号: RSI < 30 + (Pin Bar 或 吞没)
        if current_rsi < 30:
            if self.is_pinbar_bullish(df, last_index):
                signals.append({
                    'type': '做多',
                    'reason': 'RSI超卖 + 看涨Pin Bar',
                    'rsi': current_rsi,
                    'price': df.iloc[last_index]['close']
                })
            elif self.is_bullish_engulfing(df, last_index):
                signals.append({
                    'type': '做多',
                    'reason': 'RSI超卖 + 看涨吞没',
                    'rsi': current_rsi,
                    'price': df.iloc[last_index]['close']
                })
        
        return signals
    
    def send_discord_message(self, message):
        """发送Discord消息"""
        try:
            data = {
                'content': message,
                'username': 'OKX交易信号'
            }
            
            response = requests.post(self.discord_webhook, json=data)
            response.raise_for_status()
            print("Discord消息发送成功")
            
        except Exception as e:
            print(f"发送Discord消息失败: {e}")
    
    def format_signal_message(self, signals_by_timeframe):
        """格式化信号消息"""
        if not signals_by_timeframe:
            return None
            
        message = "🚨 **交易信号检测** 🚨\n\n"
        
        for symbol, timeframes in signals_by_timeframe.items():
            message += f"**{symbol}**\n"
            
            for tf, signals in timeframes.items():
                if signals:
                    message += f"📊 {tf}:\n"
                    for signal in signals:
                        emoji = "🔴" if signal['type'] == '做空' else "🟢"
                        message += f"  {emoji} {signal['type']}: {signal['reason']}\n"
                        message += f"  📈 RSI: {signal['rsi']:.2f}\n"
                        message += f"  💰 价格: {signal['price']}\n"
            message += "\n"
        
        message += f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return message
    
    def scan_all_pairs(self):
        """扫描所有交易对"""
        print("开始获取交易量前200的交易对...")
        top_pairs = self.get_top_volume_pairs(200)
        print(f"获取到 {len(top_pairs)} 个交易对")
        
        if not top_pairs:
            return
        
        signals_found = {}
        
        for i, symbol in enumerate(top_pairs):
            print(f"扫描进度: {i+1}/{len(top_pairs)} - {symbol}")
            
            symbol_signals = {}
            
            # 扫描所有时间级别
            for tf_name, tf_value in self.timeframes.items():
                try:
                    signals = self.analyze_symbol(symbol, tf_value)
                    if signals:
                        symbol_signals[tf_name] = signals
                    
                    # 避免API限制
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"分析 {symbol} {tf_name} 时出错: {e}")
                    continue
            
            if symbol_signals:
                signals_found[symbol] = symbol_signals
        
        # 发送结果
        if signals_found:
            message = self.format_signal_message(signals_found)
            if message:
                print("\n发现交易信号:")
                print(message)
                self.send_discord_message(message)
        else:
            print("未发现符合条件的交易信号")
    
    def run_continuous_scan(self, interval_minutes=30):
        """持续扫描"""
        print(f"开始持续扫描，每 {interval_minutes} 分钟扫描一次...")
        
        while True:
            try:
                print(f"\n{'='*50}")
                print(f"开始扫描 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*50}")
                
                self.scan_all_pairs()
                
                print(f"\n扫描完成，等待 {interval_minutes} 分钟后继续...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n用户中断扫描")
                break
            except Exception as e:
                print(f"扫描过程中出错: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续

def main():
    scanner = OKXScanner()
    
    print("OKX交易对扫描器启动")
    print("支持的时间级别: 5分钟, 15分钟, 1小时, 4小时, 1天")
    print("扫描条件: RSI超买超卖 + K线反转形态")
    
    # 可以选择单次扫描或持续扫描
    choice = input("\n选择模式 (1: 单次扫描, 2: 持续扫描): ")
    
    if choice == '1':
        scanner.scan_all_pairs()
    elif choice == '2':
        interval = input("输入扫描间隔(分钟，默认30): ")
        try:
            interval = int(interval) if interval else 30
        except:
            interval = 30
        scanner.run_continuous_scan(interval)
    else:
        print("无效选择")

if __name__ == "__main__":
    main()