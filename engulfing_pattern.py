#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX 顶流交易对 · 吞没扫描 · Discord 极简推送
Designed with  minimalism in mind – 加强版 (robust).
"""

import os, asyncio, aiohttp, ccxt, sys, traceback
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Optional

# ── 环境变量 ──────────────────────────────────────────────
load_dotenv()
WEBHOOK   = os.getenv("DISCORD_WEBHOOK_RSI")
API_KEY   = os.getenv("OKX_API_KEY")
API_SEC   = os.getenv("OKX_API_SECRET")
PASSPHRASE= os.getenv("OKX_PASSPHRASE")

# ── 常量 ──────────────────────────────────────────────────
TOP_N              = 100
TIMEFRAMES         = ["5m", "15m", "1h", "4h", "1d"]
SCAN_INTERVAL_MIN  = 5          # 每 15 分钟跑一次
BATCH_SIZE         = 20          # 并发请求批量
APPLE_SPACE_GRAY   = 0x1F1F1F    # 深空灰
MIN_VOLUME_USDT    = 100000      # 最小成交量阈值
ENGULF_RATIO       = 1.1         # 吞没比例阈值

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
def engulf(prev_o: float, prev_c: float, cur_o: float, cur_c: float) -> Optional[str]:
    """检测吞没形态
    
    Args:
        prev_o: 前一根K线开盘价
        prev_c: 前一根K线收盘价
        cur_o: 当前K线开盘价
        cur_c: 当前K线收盘价
        
    Returns:
        "Bullish" / "Bearish" / None
    """
    body_prev = abs(prev_c - prev_o)
    body_cur = abs(cur_c - cur_o)
    
    # 前一根K线实体太小或当前K线实体不够大
    if body_prev == 0 or body_cur < body_prev * ENGULF_RATIO:
        return None
        
    # 看涨吞没：前阴后阳，且完全包含
    if prev_c < prev_o and cur_c > cur_o and cur_c >= prev_o and cur_o <= prev_c:
        return "Bullish"
        
    # 看跌吞没：前阳后阴，且完全包含
    if prev_c > prev_o and cur_c < cur_o and cur_o >= prev_c and cur_c <= prev_o:
        return "Bearish"
        
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
                json={"embeds": embeds[:10], "username": "Engulf-Bot"}  # Discord限制最多10个embeds
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
        symbol_volumes[symbol] = quote_volume  # 保存成交量信息

    print(f"过滤后的交易对数量: {len(filtered_tickers)}")
    
    # 获取成交量TOP N
    top = sorted(filtered_tickers, key=lambda x: x[1], reverse=True)[:TOP_N]
    symbols = [s for s, _ in top]
    
    print(f"扫描TOP {len(symbols)}个交易对")

    results = []  # (tf, pattern, symbol, volume)

    async def fetch_symbol(sym: str) -> None:
        """获取单个交易对的K线数据并检测形态"""
        for tf in TIMEFRAMES:
            try:
                # 获取最近3根K线（多获取一根作为备份）
                ohlcv = await asyncio.to_thread(okx.fetch_ohlcv, sym, timeframe=tf, limit=3)
                if len(ohlcv) < 2:
                    continue
                    
                prev, cur = ohlcv[-2], ohlcv[-1]
                pat = engulf(prev[1], prev[4], cur[1], cur[4])
                if pat:
                    results.append((tf, pat, sym, symbol_volumes.get(sym, 0)))
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
            [(s, v) for t, p, s, v in results if t == tf and p == "Bullish"],
            key=lambda x: x[1],
            reverse=True
        )
        bears = sorted(
            [(s, v) for t, p, s, v in results if t == tf and p == "Bearish"],
            key=lambda x: x[1],
            reverse=True
        )
        
        if bulls or bears:
            desc_parts = []
            
            if bulls:
                bull_list = []
                for sym, vol in bulls:
                    bull_list.append(f"`{sym}`")
                desc_parts.append(f"**🟢 看涨 ({len(bulls)})**\n" + " ".join(bull_list))
                
            if bears:
                bear_list = []
                for sym, vol in bears:
                    bear_list.append(f"`{sym}`")
                desc_parts.append(f"**🔴 看跌 ({len(bears)})**\n" + " ".join(bear_list))
            
            embeds.append(make_embed(f"⏰ {tf} 周期", "\n\n".join(desc_parts)))

    # 添加统计信息
    if embeds:
        bull_count = sum(1 for _, p, _, _ in results if p == 'Bullish')
        bear_count = sum(1 for _, p, _, _ in results if p == 'Bearish')
        
        stats = (
            f"🟢 看涨: {bull_count} | "
            f"🔴 看跌: {bear_count} | "
            f"📊 总计: {len(results)}"
        )
        embeds.insert(0, make_embed("📊 吞没形态扫描报告", stats))
        await push_to_discord(embeds)

    print(f"{datetime.now().strftime('%F %T')} → "
          f"{'pushed' if embeds else 'no signal'} {len(results)}")

# ── 调度循环 ─────────────────────────────────────────────
async def scheduler() -> None:
    """主调度循环"""
    if not all([API_KEY, API_SEC, PASSPHRASE]):
        print("错误：OKX API 密钥未完全配置")
        return

    print("🚀 Engulf-Bot started…")
    print(f"配置：TOP_N={TOP_N}, MIN_VOLUME={MIN_VOLUME_USDT:,} USDT")
    print(f"时间周期：{', '.join(TIMEFRAMES)}")
    print(f"扫描间隔：{SCAN_INTERVAL_MIN}分钟")
    
    while True:
        try:
            now = datetime.now(timezone.utc)  # 使用UTC时间
            
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
