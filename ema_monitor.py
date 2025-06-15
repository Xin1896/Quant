import ccxt
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime
import time
import requests
import schedule

# 加载环境变量
load_dotenv()

# Discord Webhook配置
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

# OKX配置
OKX_API_KEY = os.getenv('OKX_API_KEY')
OKX_SECRET_KEY = os.getenv('OKX_SECRET_KEY')
OKX_PASSPHRASE = os.getenv('OKX_PASSPHRASE')

# 初始化OKX交易所
exchange = ccxt.okx({
    'apiKey': OKX_API_KEY,
    'secret': OKX_SECRET_KEY,
    'password': OKX_PASSPHRASE,
    'enableRateLimit': True
})

def send_discord_message(message, color=0x00ff00):
    """发送Discord消息"""
    try:
        data = {
            "embeds": [{
                "color": color,
                "description": message,
                "type": "rich"
            }]
        }
        response = requests.post(WEBHOOK_URL, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"发送Discord消息时出错: {e}")

def calculate_ema(data, period=20):
    """计算EMA指标"""
    return data.ewm(span=period, adjust=False).mean()

def get_klines(symbol, timeframe):
    """获取K线数据"""
    try:
        # 根据时间周期设置获取的K线数量
        limit = 200 if timeframe == '5m' else 100
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if len(ohlcv) < 50:  # 确保至少有50根K线
            return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except ccxt.NetworkError as e:
        print(f"网络错误 - {symbol} {timeframe}: {e}")
        return None
    except ccxt.ExchangeError as e:
        print(f"交易所错误 - {symbol} {timeframe}: {e}")
        return None
    except Exception as e:
        print(f"获取K线数据时出错 - {symbol} {timeframe}: {e}")
        return None

def check_ema_touch(symbol, timeframe):
    """检查是否有连续20根K线没有触及EMA20"""
    try:
        df = get_klines(symbol, timeframe)
        if df is None or len(df) < 50:  # 确保有足够的数据
            return None, None
        
        # 计算EMA20
        df['ema20'] = calculate_ema(df['close'], 20)
        
        # 检查每根K线是否触及EMA20
        df['touches_ema'] = ((df['high'] >= df['ema20']) & (df['low'] <= df['ema20']))
        
        # 计算连续未触及EMA20的K线数量
        df['not_touch_count'] = (~df['touches_ema']).astype(int).groupby((df['touches_ema'] != df['touches_ema'].shift()).cumsum()).cumsum()
        
        # 获取最新的连续未触及数量
        latest_count = df['not_touch_count'].iloc[-1]
        
        # 判断是高于还是低于EMA20
        is_above = df['close'].iloc[-1] > df['ema20'].iloc[-1]
        
        return latest_count, is_above
    except Exception as e:
        print(f"处理{symbol} {timeframe}时出错: {e}")
        return None, None

def get_top_volume_symbols(limit=100):
    """获取24小时交易量排名前100的交易对"""
    try:
        # 获取所有USDT交易对的24小时行情
        markets = exchange.load_markets()
        usdt_symbols = [symbol for symbol in markets.keys() if symbol.endswith('/USDT')]
        
        # 获取24小时行情数据
        tickers = exchange.fetch_tickers(usdt_symbols)
        
        # 创建交易量数据框
        volume_data = []
        for symbol, ticker in tickers.items():
            if 'quoteVolume' in ticker and ticker['quoteVolume'] is not None:
                # 24小时交易量（以USDT计算）
                volume_usdt = ticker['quoteVolume']
                volume_data.append({
                    'symbol': symbol,
                    'volume': volume_usdt,
                    'volume_display': f"{volume_usdt/1000000:.1f}M USDT" if volume_usdt >= 1000000 else f"{volume_usdt/1000:.1f}K USDT"
                })
        
        # 转换为DataFrame并按24小时交易量排序
        df = pd.DataFrame(volume_data)
        df = df.sort_values('volume', ascending=False)
        
        # 获取前100个交易对及其交易量
        top_pairs = df.head(limit).to_dict('records')
        
        # 返回交易对列表和其对应的交易量显示
        return [(pair['symbol'], pair['volume_display']) for pair in top_pairs]
    except Exception as e:
        print(f"获取交易量排名时出错: {e}")
        return []

def monitor_ema():
    """检查EMA触及情况"""
    print(f"开始检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    symbol_data = get_top_volume_symbols()
    if not symbol_data:
        error_message = "无法获取交易对列表，跳过本次检查"
        print(error_message)
        send_discord_message(error_message, color=0xff0000)
        return

    # 存储警报信息
    alerts_5m_above = []
    alerts_5m_below = []
    alerts_1h_above = []
    alerts_1h_below = []

    for symbol, volume_display in symbol_data:
        try:
            # 检查5分钟K线
            count_5m, is_above_5m = check_ema_touch(symbol, '5m')
            if count_5m is not None and count_5m >= 20:
                message = f"`{symbol:<12}`      已连续`{count_5m}`根K线 (24h成交: {volume_display})"
                if is_above_5m:
                    alerts_5m_above.append(message)
                else:
                    alerts_5m_below.append(message)
            
            # 检查1小时K线
            count_1h, is_above_1h = check_ema_touch(symbol, '1h')
            if count_1h is not None and count_1h >= 20:
                message = f"`{symbol:<12}`      已连续`{count_1h}`根K线 (24h成交: {volume_display})"
                if is_above_1h:
                    alerts_1h_above.append(message)
                else:
                    alerts_1h_below.append(message)
                
        except Exception as e:
            print(f"处理{symbol}时出错: {e}")

    # 发送5分钟K线警报
    if alerts_5m_above or alerts_5m_below:
        message = "**📊 5分钟K线 EMA20 警报**\n"
        if alerts_5m_above:
            message += "\n**🟢 价格在EMA20上方：**\n" + "\n".join(alerts_5m_above)
        if alerts_5m_below:
            message += "\n**🔴 价格在EMA20下方：**\n" + "\n".join(alerts_5m_below)
        send_discord_message(message, color=0x00ff00 if alerts_5m_above else 0xff0000)

    # 发送1小时K线警报
    if alerts_1h_above or alerts_1h_below:
        message = "**📈 1小时K线 EMA20 警报**\n"
        if alerts_1h_above:
            message += "\n**🟢 价格在EMA20上方：**\n" + "\n".join(alerts_1h_above)
        if alerts_1h_below:
            message += "\n**🔴 价格在EMA20下方：**\n" + "\n".join(alerts_1h_below)
        send_discord_message(message, color=0x00ff00 if alerts_1h_above else 0xff0000)

def main():
    symbol_data = get_top_volume_symbols()
    if not symbol_data:
        error_message = "无法获取交易对列表，程序退出"
        print(error_message)
        send_discord_message(error_message, color=0xff0000)
        return

    symbols_count = len(symbol_data)
    volume_summary = "\n".join([f"{i+1}. {symbol} - {volume}" for i, (symbol, volume) in enumerate(symbol_data[:10])])
    
    start_message = (
        f"**🤖 监控机器人已启动**\n"
        f"开始监控24小时交易量排名前{symbols_count}的交易对\n"
        f"监控周期：5分钟和1小时K线\n\n"
        f"**📊 当前成交量前10币种：**\n{volume_summary}"
    )
    print(start_message)
    send_discord_message(start_message, color=0x00ff00)
    
    # 立即执行一次
    monitor_ema()
    # 设置每5分钟执行一次
    schedule.every(5).minutes.do(monitor_ema)
    
    while True:
        schedule.run_pending()
        time.sleep(10)  # 缩短检查间隔，使定时更准确

def run_with_error_handling():
    """运行主程序并处理错误"""
    while True:
        try:
            main()
        except Exception as e:
            error_message = f"**❌ 程序发生错误**\n```{str(e)}```\n正在尝试重新启动..."
            print(error_message)
            try:
                send_discord_message(error_message, color=0xff0000)
            except:
                print("无法发送错误消息到Discord")
            time.sleep(60)  # 等待60秒后重试

if __name__ == "__main__":
    run_with_error_handling() 