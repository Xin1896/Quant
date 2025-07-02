#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX 市场价格监控器
使用公开API获取BTC和ETH的价格信息，无需API密钥
"""

import ccxt
import pandas as pd
from datetime import datetime
import time

class MarketPriceMonitor:
    def __init__(self):
        """初始化OKX交易所连接（仅公开API）"""
        self.exchange = ccxt.okx({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        print("✅ OKX 市场价格监控器初始化成功")
    
    def get_market_prices(self, symbols=['BTC/USDT', 'ETH/USDT']):
        """获取市场价格"""
        try:
            prices = {}
            for symbol in symbols:
                ticker = self.exchange.fetch_ticker(symbol)
                prices[symbol] = {
                    'symbol': symbol,
                    'last': ticker['last'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'high': ticker['high'],
                    'low': ticker['low'],
                    'volume': ticker['baseVolume'],
                    'change': ticker['change'],
                    'change_percent': ticker['percentage'],
                    'timestamp': ticker['timestamp']
                }
            return prices
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
            return None
    
    def get_order_book(self, symbol, limit=10):
        """获取订单簿信息"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            print(f"❌ 获取订单簿失败: {e}")
            return None
    
    def analyze_market_depth(self, symbol):
        """分析市场深度"""
        orderbook = self.get_order_book(symbol, limit=20)
        if not orderbook:
            return None
        
        # 分析买卖盘
        bids = orderbook['bids'][:10]  # 前10个买单
        asks = orderbook['asks'][:10]  # 前10个卖单
        
        bid_total = sum(bid[1] for bid in bids)
        ask_total = sum(ask[1] for ask in asks)
        
        # 计算买卖压力
        bid_pressure = bid_total / (bid_total + ask_total) * 100
        ask_pressure = ask_total / (bid_total + ask_total) * 100
        
        return {
            'symbol': symbol,
            'bid_pressure': bid_pressure,
            'ask_pressure': ask_pressure,
            'bid_total': bid_total,
            'ask_total': ask_total,
            'top_bid': bids[0][0] if bids else 0,
            'top_ask': asks[0][0] if asks else 0,
            'spread': (asks[0][0] - bids[0][0]) if bids and asks else 0
        }
    
    def display_price_info(self, prices):
        """显示价格信息"""
        if not prices:
            return
        
        print(f"\n📊 市场价格信息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        for symbol, price_info in prices.items():
            # 价格变化指示器
            change_emoji = "📈" if price_info['change'] > 0 else "📉" if price_info['change'] < 0 else "➡️"
            change_color = "🟢" if price_info['change'] > 0 else "🔴" if price_info['change'] < 0 else "⚪"
            
            print(f"\n{change_emoji} {symbol}")
            print(f"   💰 当前价格: ${price_info['last']:,.2f}")
            print(f"   {change_color} 24h变化: {price_info['change']:+.2f} ({price_info['change_percent']:+.2f}%)")
            print(f"   📈 24h最高: ${price_info['high']:,.2f}")
            print(f"   📉 24h最低: ${price_info['low']:,.2f}")
            print(f"   📊 24h成交量: {price_info['volume']:,.2f}")
            print(f"   🟢 买一价: ${price_info['bid']:,.2f}")
            print(f"   🔴 卖一价: ${price_info['ask']:,.2f}")
            
            # 分析市场深度
            depth = self.analyze_market_depth(symbol)
            if depth:
                spread_percent = (depth['spread'] / price_info['last']) * 100
                print(f"   📊 买卖压力: 买盘 {depth['bid_pressure']:.1f}% | 卖盘 {depth['ask_pressure']:.1f}%")
                print(f"   💸 点差: ${depth['spread']:.2f} ({spread_percent:.3f}%)")
    
    def get_market_sentiment(self, symbol):
        """获取市场情绪"""
        try:
            # 获取最近的价格数据
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=24)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 计算技术指标
            df['price_change'] = df['close'].pct_change()
            df['volume_ma'] = df['volume'].rolling(6).mean()
            
            # 市场情绪判断
            recent_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100
            volume_ratio = df['volume'].iloc[-1] / df['volume_ma'].iloc[-1] if df['volume_ma'].iloc[-1] > 0 else 1
            
            if recent_change > 2 and volume_ratio > 1.5:
                sentiment = "强烈看涨"
                emoji = "🚀"
            elif recent_change > 0.5:
                sentiment = "看涨"
                emoji = "📈"
            elif recent_change < -2 and volume_ratio > 1.5:
                sentiment = "强烈看跌"
                emoji = "📉"
            elif recent_change < -0.5:
                sentiment = "看跌"
                emoji = "🔻"
            else:
                sentiment = "横盘整理"
                emoji = "➡️"
            
            return {
                'sentiment': sentiment,
                'emoji': emoji,
                'price_change': recent_change,
                'volume_ratio': volume_ratio
            }
        except Exception as e:
            print(f"❌ 获取市场情绪失败: {e}")
            return None
    
    def monitor_prices(self, symbols=['BTC/USDT', 'ETH/USDT'], interval=30):
        """监控价格"""
        print("🚀 OKX 市场价格监控器启动")
        print("=" * 60)
        print(f"监控交易对: {', '.join(symbols)}")
        print(f"更新间隔: {interval}秒")
        print("按 Ctrl+C 停止监控")
        print("=" * 60)
        
        try:
            while True:
                # 获取价格
                prices = self.get_market_prices(symbols)
                if prices:
                    self.display_price_info(prices)
                    
                    # 显示市场情绪
                    print(f"\n📊 市场情绪分析:")
                    for symbol in symbols:
                        sentiment = self.get_market_sentiment(symbol)
                        if sentiment:
                            print(f"  {symbol}: {sentiment['emoji']} {sentiment['sentiment']}")
                            print(f"    价格变化: {sentiment['price_change']:+.2f}% | 成交量比: {sentiment['volume_ratio']:.2f}")
                
                print(f"\n⏳ {interval}秒后更新...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")

def main():
    """主函数"""
    monitor = MarketPriceMonitor()
    monitor.monitor_prices(interval=30)

if __name__ == "__main__":
    main() 