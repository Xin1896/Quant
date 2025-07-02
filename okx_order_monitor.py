#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX 挂单监控器
查看 BTC 和 ETH 的挂单情况，包括止盈和止损挂单
"""

import os
import ccxt
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time

class OKXOrderMonitor:
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
        
        print("✅ OKX API 连接初始化成功")
    
    def get_current_prices(self, symbols):
        """获取当前价格"""
        try:
            prices = {}
            for symbol in symbols:
                ticker = self.exchange.fetch_ticker(symbol)
                prices[symbol] = {
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'last': ticker['last'],
                    'high': ticker['high'],
                    'low': ticker['low']
                }
            return prices
        except Exception as e:
            print(f"❌ 获取价格失败: {e}")
            return None
    
    def get_open_orders(self, symbols):
        """获取挂单信息"""
        try:
            all_orders = {}
            for symbol in symbols:
                orders = self.exchange.fetch_open_orders(symbol)
                all_orders[symbol] = orders
            return all_orders
        except Exception as e:
            print(f"❌ 获取挂单失败: {e}")
            return None
    
    def get_order_history(self, symbols, limit=50):
        """获取订单历史"""
        try:
            all_history = {}
            for symbol in symbols:
                history = self.exchange.fetch_orders(symbol, limit=limit)
                all_history[symbol] = history
            return all_history
        except Exception as e:
            print(f"❌ 获取订单历史失败: {e}")
            return None
    
    def analyze_orders(self, orders, current_price):
        """分析挂单类型"""
        if not orders:
            return []
        
        analyzed_orders = []
        for order in orders:
            order_type = "未知"
            order_side = order['side']
            order_price = float(order['price'])
            order_amount = float(order['amount'])
            
            # 判断挂单类型
            if order_side == 'buy':
                if order_price < current_price * 0.95:  # 低于当前价格5%
                    order_type = "止损买入"
                elif order_price > current_price * 1.05:  # 高于当前价格5%
                    order_type = "止盈买入"
                else:
                    order_type = "普通买入"
            else:  # sell
                if order_price > current_price * 1.05:  # 高于当前价格5%
                    order_type = "止盈卖出"
                elif order_price < current_price * 0.95:  # 低于当前价格5%
                    order_type = "止损卖出"
                else:
                    order_type = "普通卖出"
            
            analyzed_orders.append({
                'id': order['id'],
                'symbol': order['symbol'],
                'side': order_side,
                'type': order_type,
                'price': order_price,
                'amount': order_amount,
                'total': order_price * order_amount,
                'status': order['status'],
                'datetime': order['datetime']
            })
        
        return analyzed_orders
    
    def display_order_summary(self, symbol, orders, current_price):
        """显示挂单摘要"""
        if not orders:
            print(f"\n📊 {symbol} - 无挂单")
            return
        
        print(f"\n📊 {symbol} 挂单分析")
        print("=" * 60)
        print(f"当前价格: ${current_price['last']:.2f}")
        print(f"买一价: ${current_price['bid']:.2f} | 卖一价: ${current_price['ask']:.2f}")
        print(f"24h最高: ${current_price['high']:.2f} | 24h最低: ${current_price['low']:.2f}")
        print("-" * 60)
        
        # 按类型分组
        order_types = {}
        for order in orders:
            order_type = order['type']
            if order_type not in order_types:
                order_types[order_type] = []
            order_types[order_type].append(order)
        
        # 显示各类型挂单
        for order_type, type_orders in order_types.items():
            print(f"\n🔸 {order_type} ({len(type_orders)}个):")
            total_amount = sum(order['total'] for order in type_orders)
            print(f"   总金额: ${total_amount:.2f}")
            
            for order in type_orders:
                emoji = "🟢" if order['side'] == 'buy' else "🔴"
                print(f"   {emoji} {order['side'].upper()} ${order['price']:.2f} x {order['amount']:.4f} = ${order['total']:.2f}")
    
    def display_detailed_orders(self, symbol, orders):
        """显示详细挂单信息"""
        if not orders:
            return
        
        print(f"\n📋 {symbol} 详细挂单信息")
        print("=" * 80)
        
        # 创建DataFrame用于显示
        df_data = []
        for order in orders:
            df_data.append({
                '订单ID': order['id'][:8] + '...',
                '方向': order['side'].upper(),
                '类型': order['type'],
                '价格': f"${order['price']:.2f}",
                '数量': f"{order['amount']:.4f}",
                '总额': f"${order['total']:.2f}",
                '状态': order['status'],
                '时间': datetime.fromtimestamp(order['datetime']/1000).strftime('%m-%d %H:%M')
            })
        
        df = pd.DataFrame(df_data)
        print(df.to_string(index=False))
    
    def monitor_orders(self, symbols=['BTC/USDT', 'ETH/USDT']):
        """监控挂单"""
        print("🔍 OKX 挂单监控器启动")
        print("=" * 50)
        
        # 获取当前价格
        print("📈 获取当前价格...")
        prices = self.get_current_prices(symbols)
        if not prices:
            return
        
        # 获取挂单
        print("📋 获取挂单信息...")
        open_orders = self.get_open_orders(symbols)
        if not open_orders:
            print("❌ 无法获取挂单信息")
            return
        
        # 分析并显示结果
        for symbol in symbols:
            current_price = prices[symbol]
            orders = open_orders[symbol]
            
            # 分析挂单类型
            analyzed_orders = self.analyze_orders(orders, current_price['last'])
            
            # 显示摘要
            self.display_order_summary(symbol, analyzed_orders, current_price)
            
            # 显示详细信息
            self.display_detailed_orders(symbol, analyzed_orders)
        
        # 统计信息
        print("\n📊 总体统计")
        print("=" * 50)
        total_orders = sum(len(orders) for orders in open_orders.values())
        print(f"总挂单数量: {total_orders}")
        
        for symbol in symbols:
            orders = open_orders[symbol]
            buy_orders = [o for o in orders if o['side'] == 'buy']
            sell_orders = [o for o in orders if o['side'] == 'sell']
            
            print(f"{symbol}: 买入挂单 {len(buy_orders)}个, 卖出挂单 {len(sell_orders)}个")

def main():
    """主函数"""
    monitor = OKXOrderMonitor()
    if monitor.exchange:
        monitor.monitor_orders()

if __name__ == "__main__":
    main() 