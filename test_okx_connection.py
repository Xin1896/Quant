#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API 连接测试脚本
用于验证API连接和权限是否正确
"""

import os
import ccxt
from dotenv import load_dotenv

def test_okx_connection():
    """测试OKX API连接"""
    print("🔍 OKX API 连接测试")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    api_key = os.getenv("OKX_API_KEY")
    api_secret = os.getenv("OKX_API_SECRET")
    passphrase = os.getenv("OKX_PASSPHRASE")
    
    # 检查环境变量
    print("📋 环境变量检查:")
    print(f"  API Key: {'✅ 已设置' if api_key else '❌ 未设置'}")
    print(f"  API Secret: {'✅ 已设置' if api_secret else '❌ 未设置'}")
    print(f"  Passphrase: {'✅ 已设置' if passphrase else '❌ 未设置'}")
    
    if not all([api_key, api_secret, passphrase]):
        print("\n❌ 环境变量未完全设置，请检查 .env 文件")
        return False
    
    # 初始化交易所
    try:
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
        print("\n✅ 交易所对象初始化成功")
    except Exception as e:
        print(f"\n❌ 交易所初始化失败: {e}")
        return False
    
    # 测试基本API调用
    tests = [
        ("获取服务器时间", lambda: exchange.fetch_time()),
        ("获取交易对信息", lambda: exchange.fetch_ticker('BTC/USDT')),
        ("获取账户余额", lambda: exchange.fetch_balance()),
        ("获取挂单", lambda: exchange.fetch_open_orders('BTC/USDT')),
    ]
    
    print("\n🧪 API 功能测试:")
    for test_name, test_func in tests:
        try:
            result = test_func()
            print(f"  {test_name}: ✅ 成功")
            if test_name == "获取交易对信息":
                print(f"    BTC/USDT 当前价格: ${result['last']:.2f}")
            elif test_name == "获取账户余额":
                total_balance = sum(float(balance['total']) for balance in result.values() if isinstance(balance, dict) and 'total' in balance)
                print(f"    账户总余额: {total_balance:.2f}")
            elif test_name == "获取挂单":
                print(f"    当前挂单数量: {len(result)}")
        except Exception as e:
            print(f"  {test_name}: ❌ 失败 - {e}")
    
    print("\n✅ 连接测试完成")
    return True

def show_usage_tips():
    """显示使用提示"""
    print("\n💡 使用提示:")
    print("1. 确保 .env 文件包含正确的API凭据")
    print("2. 确保API密钥具有交易权限")
    print("3. 检查网络连接是否正常")
    print("4. 如果遇到频率限制，请稍后重试")
    
    print("\n🚀 运行监控器:")
    print("  基础监控: python okx_order_monitor.py")
    print("  高级监控: python okx_advanced_monitor.py")

if __name__ == "__main__":
    success = test_okx_connection()
    show_usage_tips()
    
    if success:
        print("\n🎉 所有测试通过！可以开始使用监控器了")
    else:
        print("\n⚠️  请解决上述问题后再使用监控器") 