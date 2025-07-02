#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX 高级挂单监控器
实时监控 BTC 和 ETH 的挂单情况，包含详细的止盈止损分析
"""

import os
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import threading
from collections import defaultdict

class OKXAdvancedMonitor:
    def __init__(self):
        """初始化OKX交易所连接"""
        load_dotenv()
        
        self.api_key = os.getenv("OKX_API_KEY")
        self.api_secret = os.getenv("OKX_API_SECRET")
        self.passphrase = os.getenv("OKX_PASSPHRASE")
        
        if not all([self.api_key, self.api_secret, self.passphrase]):
            print("❌ OKX API 凭据未在环境变量中设置")
            print("请设置以下环境变量：")
            print("  - OKX_API_KEY")
            print("  - OKX_API_SECRET") 
            print("  - OKX_PASSPHRASE")
            return None
            
        self.exchange = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
                'adjustForTimeDifference': True
            }
        })
        
        # 数据存储
        self.price_history = defaultdict(list)
        self.order_history = defaultdict(list)
        self.monitoring = False
        
        print("✅ OKX 高级监控器初始化成功")
    
    def get_account_balance(self):
        """获取账户余额"""
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            print(f"❌ 获取账户余额失败: {e}")
            return None
    
    def get_position_info(self, symbols):
        """获取持仓信息"""
        try:
            positions = {}
            for symbol in symbols:
                # 获取现货持仓
                balance = self.exchange.fetch_balance()
                base_currency = symbol.split('/')[0]  # BTC, ETH
                quote_currency = symbol.split('/')[1]  # USDT
                
                base_balance = balance.get(base_currency, {}).get('free', 0)
                quote_balance = balance.get(quote_currency, {}).get('free', 0)
                
                positions[symbol] = {
                    'base_balance': base_balance,
                    'quote_balance': quote_balance,
                    'base_currency': base_currency,
                    'quote_currency': quote_currency
                }
            return positions
        except Exception as e:
            print(f"❌ 获取持仓信息失败: {e}")
            return None
    
    def get_market_depth(self, symbol, limit=20):
        """获取市场深度"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            return orderbook
        except Exception as e:
            print(f"❌ 获取市场深度失败: {e}")
            return None
    
    def analyze_stop_loss_take_profit(self, orders, current_price, position_info):
        """详细分析止盈止损挂单"""
        if not orders:
            return []
        
        analyzed_orders = []
        for order in orders:
            order_side = order['side']
            order_price = float(order['price'])
            order_amount = float(order['amount'])
            current_price_val = float(current_price['last'])
            
            # 计算价格偏离百分比
            price_deviation = ((order_price - current_price_val) / current_price_val) * 100
            
            # 判断挂单类型和策略
            order_type = "未知"
            strategy = "未知"
            risk_level = "低"
            
            if order_side == 'buy':
                if price_deviation < -10:
                    order_type = "深度止损买入"
                    strategy = "抄底策略"
                    risk_level = "高"
                elif price_deviation < -5:
                    order_type = "止损买入"
                    strategy = "回调买入"
                    risk_level = "中"
                elif price_deviation < -2:
                    order_type = "支撑位买入"
                    strategy = "技术支撑"
                    risk_level = "中"
                elif price_deviation < 2:
                    order_type = "市价附近买入"
                    strategy = "即时买入"
                    risk_level = "低"
                elif price_deviation < 5:
                    order_type = "突破买入"
                    strategy = "突破策略"
                    risk_level = "中"
                else:
                    order_type = "追高买入"
                    strategy = "追涨策略"
                    risk_level = "高"
            else:  # sell
                if price_deviation > 10:
                    order_type = "深度止盈卖出"
                    strategy = "获利了结"
                    risk_level = "低"
                elif price_deviation > 5:
                    order_type = "止盈卖出"
                    strategy = "获利了结"
                    risk_level = "低"
                elif price_deviation > 2:
                    order_type = "阻力位卖出"
                    strategy = "技术阻力"
                    risk_level = "中"
                elif price_deviation < -2:
                    order_type = "止损卖出"
                    strategy = "风险控制"
                    risk_level = "高"
                else:
                    order_type = "市价附近卖出"
                    strategy = "即时卖出"
                    risk_level = "低"
            
            # 计算潜在盈亏
            potential_pnl = 0
            if order_side == 'buy':
                potential_pnl = (current_price_val - order_price) * order_amount
            else:
                potential_pnl = (order_price - current_price_val) * order_amount
            
            analyzed_orders.append({
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order_side,
                'type': order_type,
                'strategy': strategy,
                'risk_level': risk_level,
                'price': order_price,
                'amount': order_amount,
                'total': order_price * order_amount,
                'current_price': current_price_val,
                'price_deviation': price_deviation,
                'potential_pnl': potential_pnl,
                'status': order['status'],
                'datetime': order['datetime']
            })
        
        return analyzed_orders
    
    def display_advanced_analysis(self, symbol, orders, current_price, position_info):
        """显示高级分析结果"""
        if not orders:
            print(f"\n📊 {symbol} - 无挂单")
            return
        
        print(f"\n🔍 {symbol} 高级挂单分析")
        print("=" * 80)
        
        # 价格信息
        print(f"💰 当前价格: ${current_price['last']:.2f}")
        print(f"📈 24h最高: ${current_price['high']:.2f} | 📉 24h最低: ${current_price['low']:.2f}")
        print(f"🟢 买一价: ${current_price['bid']:.2f} | 🔴 卖一价: ${current_price['ask']:.2f}")
        
        # 持仓信息
        if position_info and symbol in position_info:
            pos = position_info[symbol]
            print(f"💼 持仓: {pos['base_balance']:.4f} {pos['base_currency']} | {pos['quote_balance']:.2f} {pos['quote_currency']}")
        
        print("-" * 80)
        
        # 按策略分组显示
        strategy_groups = defaultdict(list)
        for order in orders:
            strategy_groups[order['strategy']].append(order)
        
        total_potential_pnl = 0
        total_order_value = 0
        
        for strategy, strategy_orders in strategy_groups.items():
            print(f"\n🎯 {strategy} ({len(strategy_orders)}个挂单):")
            
            strategy_pnl = 0
            strategy_value = 0
            
            for order in strategy_orders:
                emoji = "🟢" if order['side'] == 'buy' else "🔴"
                risk_emoji = {"低": "🟢", "中": "🟡", "高": "🔴"}[order['risk_level']]
                
                print(f"   {emoji} {order['side'].upper()} ${order['price']:.2f} x {order['amount']:.4f}")
                print(f"     类型: {order['type']} | 风险: {risk_emoji} {order['risk_level']}")
                print(f"     偏离: {order['price_deviation']:+.2f}% | 潜在盈亏: ${order['potential_pnl']:+.2f}")
                print(f"     总额: ${order['total']:.2f}")
                print()
                
                strategy_pnl += order['potential_pnl']
                strategy_value += order['total']
            
            print(f"   📊 策略总计: ${strategy_value:.2f} | 潜在盈亏: ${strategy_pnl:+.2f}")
            total_potential_pnl += strategy_pnl
            total_order_value += strategy_value
        
        print(f"\n📈 总体统计:")
        print(f"   总挂单价值: ${total_order_value:.2f}")
        print(f"   总潜在盈亏: ${total_potential_pnl:+.2f}")
        print(f"   盈亏比例: {(total_potential_pnl/total_order_value*100):+.2f}%" if total_order_value > 0 else "   盈亏比例: N/A")
    
    def get_market_sentiment(self, symbol):
        """获取市场情绪指标"""
        try:
            # 获取最近的价格数据
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=24)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 计算简单的技术指标
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
    
    def monitor_orders_advanced(self, symbols=['BTC/USDT', 'ETH/USDT'], interval=30):
        """高级挂单监控"""
        print("🚀 OKX 高级挂单监控器启动")
        print("=" * 60)
        print(f"监控交易对: {', '.join(symbols)}")
        print(f"更新间隔: {interval}秒")
        print("按 Ctrl+C 停止监控")
        print("=" * 60)
        
        self.monitoring = True
        
        try:
            while self.monitoring:
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 60)
                
                # 获取当前价格
                prices = self.get_current_prices(symbols)
                if not prices:
                    continue
                
                # 获取持仓信息
                positions = self.get_position_info(symbols)
                
                # 获取挂单
                open_orders = self.get_open_orders(symbols)
                if not open_orders:
                    print("❌ 无法获取挂单信息")
                    time.sleep(interval)
                    continue
                
                # 分析每个交易对
                for symbol in symbols:
                    current_price = prices[symbol]
                    orders = open_orders[symbol]
                    position_info = positions[symbol] if positions else None
                    
                    # 获取市场情绪
                    sentiment = self.get_market_sentiment(symbol)
                    
                    # 分析挂单
                    analyzed_orders = self.analyze_stop_loss_take_profit(orders, current_price, position_info)
                    
                    # 显示分析结果
                    self.display_advanced_analysis(symbol, analyzed_orders, current_price, position_info)
                    
                    # 显示市场情绪
                    if sentiment:
                        print(f"📊 市场情绪: {sentiment['emoji']} {sentiment['sentiment']}")
                        print(f"   价格变化: {sentiment['price_change']:+.2f}% | 成交量比: {sentiment['volume_ratio']:.2f}")
                
                # 等待下次更新
                print(f"\n⏳ {interval}秒后更新...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
            self.monitoring = False
    
    def get_order_statistics(self, symbols):
        """获取挂单统计信息"""
        try:
            stats = {}
            for symbol in symbols:
                orders = self.exchange.fetch_open_orders(symbol)
                
                buy_orders = [o for o in orders if o['side'] == 'buy']
                sell_orders = [o for o in orders if o['side'] == 'sell']
                
                buy_total = sum(float(o['price']) * float(o['amount']) for o in buy_orders)
                sell_total = sum(float(o['price']) * float(o['amount']) for o in sell_orders)
                
                stats[symbol] = {
                    'total_orders': len(orders),
                    'buy_orders': len(buy_orders),
                    'sell_orders': len(sell_orders),
                    'buy_total': buy_total,
                    'sell_total': sell_total,
                    'order_imbalance': buy_total - sell_total
                }
            
            return stats
        except Exception as e:
            print(f"❌ 获取挂单统计失败: {e}")
            return None

def main():
    """主函数"""
    monitor = OKXAdvancedMonitor()
    if monitor.exchange:
        # 运行高级监控
        monitor.monitor_orders_advanced(interval=30)

if __name__ == "__main__":
    main() 