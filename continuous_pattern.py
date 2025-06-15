#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX 顶流交易对 · 连续K线形态扫描 · Discord 极简推送
检测连续3根及以上的阳线或阴线，第二根和第三根影线很短
"""

import os, asyncio, aiohttp, ccxt, sys, traceback
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Optional

# ── 环境变量 ──────────────────────────────────────────────
load_dotenv()
WEBHOOK   = os.getenv("DISCORD_WEBHOOK_TREND")
API_KEY   = os.getenv("OKX_API_KEY")
API_SEC   = os.getenv("OKX_API_SECRET")
PASSPHRASE= os.getenv("OKX_PASSPHRASE")

# ── 常量 ──────────────────────────────────────────────────
TOP_N              = 100
TIMEFRAMES         = ["5m", "15m", "1h", "4h", "1d"]
SCAN_INTERVAL_MIN  = 5           # 每 5 分钟跑一次
BATCH_SIZE         = 20          # 并发请求批量
APPLE_SPACE_GRAY   = 0x1F1F1F    # 深空灰
MIN_VOLUME_USDT    = 100000      # 最小成交量阈值
MIN_CANDLES        = 3           # 最少连续K线数量
MAX_SHADOW_RATIO   = 0.2         # 影线占K线全长的最大比例

# ── 交易所实例 ────────────────────────────────────────────
okx = ccxt.okx({
    "apiKey": API_KEY,
    "secret": API_SEC,
    "password": PASSPHRASE,
    "enableRateLimit": True,
    "options": {
        "defaultType": "spot",
        "adjustForTimeDifference": True
    }
})

# ── 技术形态检测 ───────────────────────────────────────────
def detect_continuous_pattern(ohlcv_list: List[List]) -> Optional[Tuple[str, int]]:
    """检测连续阳线或阴线形态
    
    Args:
        ohlcv_list: K线数据列表，每个元素为 [timestamp, open, high, low, close, volume]
        
    Returns:
        (pattern_type, count) 或 None
        pattern_type: "Bullish" (连续阳线) 或 "Bearish" (连续阴线)
        count: 连续K线数量
    """
    if len(ohlcv_list) < MIN_CANDLES:
        return None
    
    # 检查最近的K线是否形成连续形态
    bullish_count = 0
    bearish_count = 0
    
    for i in range(len(ohlcv_list) - 1, -1, -1):
        candle = ohlcv_list[i]
        open_price, high_price, low_price, close_price = candle[1], candle[2], candle[3], candle[4]
        
        # 计算K线实体和全长
        body = abs(close_price - open_price)
        full_length = high_price - low_price
        
        if full_length == 0:
            break
            
        # 计算上下影线
        if close_price > open_price:  # 阳线
            upper_shadow = high_price - close_price
            lower_shadow = open_price - low_price
        else:  # 阴线
            upper_shadow = high_price - open_price
            lower_shadow = close_price - low_price
        
        # 计算影线比例
        shadow_ratio = (upper_shadow + lower_shadow) / full_length
        
        # 判断K线类型
        is_bullish = close_price > open_price
        is_bearish = close_price < open_price
        
        # 对于第一根K线，不检查影线
        if i == len(ohlcv_list) - 1:
            if is_bullish:
                bullish_count = 1
                bearish_count = 0
            elif is_bearish:
                bearish_count = 1
                bullish_count = 0
            else:
                break
        else:
            # 对于后续K线，检查影线长度
            if bullish_count > 0:
                if is_bullish and (bullish_count == 1 or shadow_ratio <= MAX_SHADOW_RATIO):
                    bullish_count += 1
                else:
                    break
            elif bearish_count > 0:
                if is_bearish and (bearish_count == 1 or shadow_ratio <= MAX_SHADOW_RATIO):
                    bearish_count += 1
                else:
                    break
    
    # 返回结果
    if bullish_count >= MIN_CANDLES:
        return ("Bullish", bullish_count)
    elif bearish_count >= MIN_CANDLES:
        return ("Bearish", bearish_count)
    
    return None

# ── Discord 推送 ─────────────────────────────────────────
async def push_to_discord(embeds: List[Dict]) -> None:
    """推送消息到Discord"""
    if not WEBHOOK or not embeds:
        return
        
    try:
        async with aiohttp.ClientSession() as sess:
            resp = await sess.post(
                WEBHOOK,
                json={"embeds": embeds[:10], "username": "连续K线机器人"}
            )
            if resp.status != 204:
                print(f"Discord Error: {resp.status}", file=sys.stderr)
    except Exception:
        traceback.print_exc()

def make_embed(title: str, desc: str, color: int = APPLE_SPACE_GRAY) -> Dict:
    """创建Discord embed对象"""
    return {
        "title": title,
        "description": desc,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ── 扫描一次 ─────────────────────────────────────────────
async def scan_once() -> None:
    """执行一次扫描"""
    try:
        # 1) 获取所有交易对行情
        tickers = await asyncio.to_thread(okx.fetch_tickers)
    except Exception:
        traceback.print_exc()
        return

    # 过滤交易对
    filtered_tickers = []
    symbol_volumes = {}  # 保存每个交易对的成交量
    
    for symbol, ticker in tickers.items():
        if not symbol.endswith("/USDT"):
            continue
            
        quote_volume = ticker.get("quoteVolume", 0)
        if quote_volume < MIN_VOLUME_USDT:
            continue
            
        filtered_tickers.append((symbol, quote_volume))
        symbol_volumes[symbol] = quote_volume

    print(f"过滤后的交易对数量: {len(filtered_tickers)}")
    
    # 获取成交量TOP N
    top = sorted(filtered_tickers, key=lambda x: x[1], reverse=True)[:TOP_N]
    symbols = [s for s, _ in top]
    
    print(f"扫描TOP {len(symbols)}个交易对")

    results = []  # (tf, pattern, symbol, count, volume)

    async def fetch_symbol(sym: str) -> None:
        """获取单个交易对的K线数据并检测形态"""
        for tf in TIMEFRAMES:
            try:
                # 获取最近10根K线，以便检测更长的连续形态
                ohlcv = await asyncio.to_thread(okx.fetch_ohlcv, sym, timeframe=tf, limit=10)
                if len(ohlcv) < MIN_CANDLES:
                    continue
                    
                result = detect_continuous_pattern(ohlcv)
                if result:
                    pattern, count = result
                    results.append((tf, pattern, sym, count, symbol_volumes.get(sym, 0)))
            except Exception as e:
                # 只在调试时打印错误
                if os.getenv("DEBUG"):
                    print(f"{sym} {tf}: {type(e).__name__}: {e}")

    # 2) 并发批量处理
    for i in range(0, len(symbols), BATCH_SIZE):
        batch = symbols[i:i + BATCH_SIZE]
        tasks = [fetch_symbol(s) for s in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.sleep(0.25)  # 避免请求过快

    # 3) 组装Discord消息
    embeds = []
    
    # 按时间周期分组
    for tf in TIMEFRAMES:
        # 按成交量排序
        bulls = sorted(
            [(s, c, v) for t, p, s, c, v in results if t == tf and p == "Bullish"],
            key=lambda x: x[2],
            reverse=True
        )
        bears = sorted(
            [(s, c, v) for t, p, s, c, v in results if t == tf and p == "Bearish"],
            key=lambda x: x[2],
            reverse=True
        )
        
        if bulls or bears:
            desc_parts = []
            
            if bulls:
                bull_list = []
                for sym, count, vol in bulls:
                    bull_list.append(f"`{sym}` ({count}根)")
                desc_parts.append(f"**🟢 连续阳线 ({len(bulls)})**\n" + " ".join(bull_list))
                
            if bears:
                bear_list = []
                for sym, count, vol in bears:
                    bear_list.append(f"`{sym}` ({count}根)")
                desc_parts.append(f"**🔴 连续阴线 ({len(bears)})**\n" + " ".join(bear_list))
            
            embeds.append(make_embed(f"⏰ {tf} 周期", "\n\n".join(desc_parts)))

    # 添加统计信息
    if embeds:
        bull_count = sum(1 for _, p, _, _, _ in results if p == 'Bullish')
        bear_count = sum(1 for _, p, _, _, _ in results if p == 'Bearish')
        
        stats = (
            f"🟢 连续阳线: {bull_count} | "
            f"🔴 连续阴线: {bear_count} | "
            f"📊 总计: {len(results)}"
        )
        
        # 添加说明
        desc = f"{stats}\n\n"
        desc += "**检测规则：**\n"
        desc += f"• 至少连续{MIN_CANDLES}根同向K线\n"
        desc += f"• 第2根起影线占比不超过{MAX_SHADOW_RATIO*100:.0f}%"
        
        embeds.insert(0, make_embed("📊 连续K线形态扫描报告", desc))
        await push_to_discord(embeds)

    print(f"{datetime.now().strftime('%F %T')} → "
          f"{'pushed' if embeds else 'no signal'} {len(results)}")

# ── 调度循环 ─────────────────────────────────────────────
async def scheduler() -> None:
    """主调度循环"""
    if not all([API_KEY, API_SEC, PASSPHRASE]):
        print("错误：OKX API 密钥未完全配置")
        return

    print("🚀 连续K线形态机器人启动…")
    print(f"配置：TOP_N={TOP_N}, MIN_VOLUME={MIN_VOLUME_USDT:,} USDT")
    print(f"时间周期：{', '.join(TIMEFRAMES)}")
    print(f"扫描间隔：{SCAN_INTERVAL_MIN}分钟")
    print(f"检测规则：至少{MIN_CANDLES}根连续K线，影线比例≤{MAX_SHADOW_RATIO*100:.0f}%")
    
    while True:
        try:
            now = datetime.now(timezone.utc)
            
            # 检查是否到了扫描时间
            if now.minute % SCAN_INTERVAL_MIN == 0:
                print(f"\n{'='*50}")
                print(f"开始扫描 - {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                await scan_once()
                
                # 计算下一次扫描时间
                next_scan = now.replace(second=0, microsecond=0) + timedelta(minutes=SCAN_INTERVAL_MIN)
                sleep_seconds = (next_scan - datetime.now(timezone.utc)).total_seconds()
                
                if sleep_seconds > 0:
                    print(f"下次扫描时间：{next_scan.strftime('%H:%M:%S UTC')}")
                    await asyncio.sleep(sleep_seconds)
            else:
                # 等待到下一分钟
                await asyncio.sleep(60 - now.second)
                
        except Exception:
            traceback.print_exc()
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(scheduler())
    except KeyboardInterrupt:
        print("\nBye ✌️") 