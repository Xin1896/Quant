#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API 详细诊断脚本
帮助排查API连接和权限问题
"""

import os
import ccxt
import time
from dotenv import load_dotenv

def debug_okx_api():
    """详细诊断OKX API"""
    print("🔍 OKX API 详细诊断")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    api_key = os.getenv("OKX_API_KEY")
    api_secret = os.getenv("OKX_API_SECRET")
    passphrase = os.getenv("OKX_PASSPHRASE")
    
    print("📋 环境变量详情:")
    print(f"  API Key: {api_key[:10]}...{api_key[-4:] if api_key else 'None'}")
    print(f"  API Secret: {api_secret[:10]}...{api_secret[-4:] if api_secret else 'None'}")
    print(f"  Passphrase: {passphrase[:10]}...{passphrase[-4:] if passphrase else 'None'}")
    
    if not all([api_key, api_secret, passphrase]):
        print("\n❌ 环境变量不完整")
        return False
    
    # 检查API密钥格式
    print(f"\n🔍 API密钥格式检查:")
    print(f"  API Key长度: {len(api_key)}")
    print(f"  API Secret长度: {len(api_secret)}")
    print(f"  Passphrase长度: {len(passphrase)}")
    
    # 尝试不同的配置
    configs = [
        {
            'name': '标准配置',
            'config': {
                'apiKey': api_key,
                'secret': api_secret,
                'password': passphrase,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True
                }
            }
        },
        {
            'name': '无密码配置',
            'config': {
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            }
        },
        {
            'name': '简化配置',
            'config': {
                'apiKey': api_key,
                'secret': api_secret,
                'password': passphrase,
                'enableRateLimit': True
            }
        }
    ]
    
    for config_info in configs:
        print(f"\n🧪 测试配置: {config_info['name']}")
        try:
            exchange = ccxt.okx(config_info['config'])
            
            # 测试基本连接
            print("  📡 测试基本连接...")
            server_time = exchange.fetch_time()
            print(f"    ✅ 服务器时间: {server_time}")
            
            # 测试公开API
            print("  📊 测试公开API...")
            ticker = exchange.fetch_ticker('BTC/USDT')
            print(f"    ✅ BTC价格: ${ticker['last']:.2f}")
            
            # 测试私有API
            print("  🔐 测试私有API...")
            try:
                balance = exchange.fetch_balance()
                print(f"    ✅ 账户余额获取成功")
                # 显示一些余额信息
                usdt_balance = balance.get('USDT', {}).get('free', 0)
                btc_balance = balance.get('BTC', {}).get('free', 0)
                print(f"    💰 USDT余额: {usdt_balance}")
                print(f"    ₿ BTC余额: {btc_balance}")
            except Exception as e:
                print(f"    ❌ 私有API失败: {e}")
                if "API key doesn't exist" in str(e):
                    print("    💡 提示: API密钥不存在或格式错误")
                elif "Invalid signature" in str(e):
                    print("    💡 提示: API签名错误，检查Secret Key")
                elif "Invalid passphrase" in str(e):
                    print("    💡 提示: Passphrase错误")
                continue
            
            # 测试挂单API
            print("  📋 测试挂单API...")
            try:
                orders = exchange.fetch_open_orders('BTC/USDT')
                print(f"    ✅ 挂单获取成功，数量: {len(orders)}")
            except Exception as e:
                print(f"    ❌ 挂单API失败: {e}")
            
            print(f"  ✅ {config_info['name']} 配置成功!")
            return True
            
        except Exception as e:
            print(f"  ❌ {config_info['name']} 配置失败: {e}")
            if "API key doesn't exist" in str(e):
                print("    💡 可能原因:")
                print("      1. API密钥不存在或已被删除")
                print("      2. API密钥格式错误")
                print("      3. 使用了错误的API密钥")
            elif "Invalid signature" in str(e):
                print("    💡 可能原因:")
                print("      1. API Secret Key错误")
                print("      2. 时间同步问题")
            elif "Invalid passphrase" in str(e):
                print("    💡 可能原因:")
                print("      1. Passphrase错误")
                print("      2. Passphrase格式错误")
    
    return False

def show_troubleshooting_tips():
    """显示故障排除提示"""
    print("\n🔧 故障排除指南:")
    print("=" * 60)
    
    print("\n1. 🔑 API密钥问题:")
    print("   - 登录OKX账户，检查API管理页面")
    print("   - 确认API密钥状态为'启用'")
    print("   - 检查API密钥是否有交易权限")
    print("   - 重新生成API密钥")
    
    print("\n2. 🔐 权限设置:")
    print("   - 确保勾选了'交易'权限")
    print("   - 检查IP白名单设置")
    print("   - 确认API密钥未过期")
    
    print("\n3. ⏰ 时间同步:")
    print("   - 确保系统时间准确")
    print("   - 检查时区设置")
    
    print("\n4. 🌐 网络问题:")
    print("   - 检查网络连接")
    print("   - 尝试使用VPN")
    print("   - 检查防火墙设置")
    
    print("\n5. 📝 环境变量:")
    print("   - 确保.env文件格式正确")
    print("   - 检查变量名拼写")
    print("   - 确保没有多余的空格或换行")

def test_public_api():
    """测试公开API"""
    print("\n🌐 测试公开API (无需密钥):")
    try:
        exchange = ccxt.okx()
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"  ✅ BTC/USDT 价格: ${ticker['last']:.2f}")
        print(f"  ✅ 24h最高: ${ticker['high']:.2f}")
        print(f"  ✅ 24h最低: ${ticker['low']:.2f}")
        return True
    except Exception as e:
        print(f"  ❌ 公开API失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OKX API 诊断工具")
    print("=" * 60)
    
    # 先测试公开API
    public_ok = test_public_api()
    
    # 然后测试私有API
    private_ok = debug_okx_api()
    
    show_troubleshooting_tips()
    
    if public_ok and private_ok:
        print("\n🎉 所有测试通过！API配置正确")
    elif public_ok and not private_ok:
        print("\n⚠️  公开API正常，私有API有问题，请检查API密钥配置")
    else:
        print("\n❌ 网络连接或API服务有问题") 