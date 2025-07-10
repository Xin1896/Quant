#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深300板块分析工具 - 简化版
快速分析沪深300成分股的板块分布
"""

import akshare as ak
import pandas as pd
from datetime import datetime
import time

def get_hs300_stocks_simple():
    """获取沪深300成分股列表（简化版）"""
    try:
        print("正在获取沪深300成分股列表...")
        # 获取沪深300成分股
        hs300_df = ak.index_stock_cons_weight_csindex(symbol="000300")
        print(f"成功获取 {len(hs300_df)} 只股票")
        return hs300_df
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return None

def classify_sector_simple(stock_name):
    """简单的板块分类"""
    sector_keywords = {
        '金融': ['银行', '保险', '证券', '信托', '基金'],
        '房地产': ['地产', '房地产', '建筑', '建材'],
        '科技': ['科技', '软件', '互联网', '通信', '电子', '半导体', '芯片'],
        '医药': ['医药', '生物', '医疗', '器械'],
        '消费': ['消费', '食品', '饮料', '家电', '零售', '旅游'],
        '汽车': ['汽车', '新能源'],
        '能源': ['石油', '煤炭', '电力', '燃气'],
        '原材料': ['钢铁', '有色金属', '化工'],
        '交通运输': ['航空', '港口', '物流', '铁路', '公路'],
        '工业': ['机械', '装备', '制造'],
        '农业': ['农业', '养殖', '种植']
    }
    
    for sector, keywords in sector_keywords.items():
        for keyword in keywords:
            if keyword in stock_name:
                return sector
    return '其他'

def analyze_hs300_sectors():
    """分析沪深300板块分布"""
    # 获取股票数据
    hs300_df = get_hs300_stocks_simple()
    if hs300_df is None:
        return
    
    # 添加板块分类
    print("正在分类板块...")
    hs300_df['板块'] = hs300_df['成分券名称'].apply(classify_sector_simple)
    
    # 按板块分组统计
    sector_stats = hs300_df.groupby('板块').agg({
        '成分券代码': 'count',
        '权重': 'sum'
    }).rename(columns={'成分券代码': '股票数量', '权重': '总权重'})
    
    # 按股票数量排序
    sector_stats = sector_stats.sort_values('股票数量', ascending=False)
    
    print("\n=== 沪深300板块分布 ===")
    print(f"总股票数: {len(hs300_df)}")
    print(f"板块数量: {len(sector_stats)}")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n板块统计:")
    print("-" * 50)
    
    for sector, row in sector_stats.iterrows():
        print(f"{sector:12} | {int(row['股票数量']):3d}只股票 | 权重: {row['总权重']:6.2f}%")
    
    # 生成简单的HTML报告
    generate_simple_html(hs300_df, sector_stats)

def generate_simple_html(hs300_df, sector_stats):
    """生成简单的HTML报告"""
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>沪深300板块分析</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .sector-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        .sector-table th, .sector-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .sector-table th {{
            background-color: #667eea;
            color: white;
        }}
        .sector-table tr:hover {{
            background-color: #f5f5f5;
        }}
        .stock-list {{
            margin-top: 20px;
        }}
        .stock-item {{
            display: inline-block;
            margin: 5px;
            padding: 5px 10px;
            background: #e9ecef;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>沪深300板块分析报告</h1>
        
        <div class="stats">
            <h3>总体统计</h3>
            <p>总股票数: {len(hs300_df)} | 板块数量: {len(sector_stats)} | 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <table class="sector-table">
            <thead>
                <tr>
                    <th>板块</th>
                    <th>股票数量</th>
                    <th>总权重(%)</th>
                    <th>平均权重(%)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for sector, row in sector_stats.iterrows():
        avg_weight = row['总权重'] / row['股票数量']
        html_content += f"""
                <tr>
                    <td><strong>{sector}</strong></td>
                    <td>{row['股票数量']}</td>
                    <td>{row['总权重']:.2f}</td>
                    <td>{avg_weight:.2f}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
        
        <h3>各板块股票详情</h3>
    """
    
    # 按板块显示股票列表
    for sector in sector_stats.index:
        sector_stocks = hs300_df[hs300_df['板块'] == sector]
        html_content += f"""
        <div class="stock-list">
            <h4>{sector} ({len(sector_stocks)}只股票)</h4>
        """
        
        for _, stock in sector_stocks.iterrows():
            html_content += f'<span class="stock-item">{stock["成分券代码"]} {stock["成分券名称"]}</span>'
        
        html_content += "</div>"
    
    html_content += f"""
        <div class="footer">
            <p>数据来源: akshare | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
    """
    
    filename = "hs300_simple_analysis.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nHTML报告已生成: {filename}")
    print("请在浏览器中打开查看详细结果")

def main():
    """主函数"""
    print("=== 沪深300板块分析工具 ===")
    analyze_hs300_sectors()

if __name__ == "__main__":
    main() 