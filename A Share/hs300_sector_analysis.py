#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深300板块分析工具
分析沪深300成分股的板块分布，按市值排序显示结果
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

class HS300SectorAnalyzer:
    def __init__(self):
        self.hs300_stocks = None
        self.sector_data = {}
        self.html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>沪深300板块分析报告</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .sector-section {
            margin: 30px;
        }
        .sector-header {
            background: #667eea;
            color: white;
            padding: 15px 20px;
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .sector-name {
            font-size: 1.3em;
            font-weight: bold;
        }
        .sector-count {
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .stock-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }
        .stock-table th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }
        .stock-table td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .stock-table tr:hover {
            background: #f8f9fa;
        }
        .market-cap {
            font-weight: bold;
            color: #28a745;
        }
        .stock-code {
            font-family: 'Courier New', monospace;
            color: #495057;
        }
        .stock-name {
            font-weight: 500;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #eee;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 2em; }
            .stats { grid-template-columns: 1fr; }
            .sector-section { margin: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>沪深300板块分析报告</h1>
            <p>基于实时市场数据的板块分布与市值排序分析</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_stocks}</div>
                <div class="stat-label">总股票数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_sectors}</div>
                <div class="stat-label">板块数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_market_cap}</div>
                <div class="stat-label">总市值(亿元)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{update_time}</div>
                <div class="stat-label">更新时间</div>
            </div>
        </div>
        
        {sector_content}
        
        <div class="footer">
            <p>数据来源: akshare | 生成时间: {current_time}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def get_hs300_stocks(self):
        """获取沪深300成分股列表"""
        try:
            print("正在获取沪深300成分股列表...")
            # 获取沪深300成分股
            hs300_df = ak.index_stock_cons_weight_csindex(symbol="000300")
            
            # 获取股票基本信息
            stock_list = []
            for _, row in hs300_df.iterrows():
                try:
                    stock_code = row['成分券代码']
                    stock_name = row['成分券名称']
                    weight = row['权重']
                    
                    # 获取股票详细信息
                    stock_info = ak.stock_individual_info_em(symbol=stock_code)
                    
                    # 提取市值信息
                    market_cap = 0
                    sector = "未知"
                    
                    if not stock_info.empty:
                        # 查找市值信息
                        for _, info_row in stock_info.iterrows():
                            if '总市值' in str(info_row['item']) or '市值' in str(info_row['item']):
                                try:
                                    market_cap_str = str(info_row['value'])
                                    if '亿' in market_cap_str:
                                        market_cap = float(market_cap_str.replace('亿', '').replace(',', ''))
                                    elif '万' in market_cap_str:
                                        market_cap = float(market_cap_str.replace('万', '').replace(',', '')) / 10000
                                    else:
                                        market_cap = float(market_cap_str.replace(',', '')) / 100000000
                                    break
                                except:
                                    continue
                    
                    # 获取行业信息
                    try:
                        industry_info = ak.stock_board_industry_name_em()
                        # 这里需要根据股票代码匹配行业，简化处理
                        sector = "金融" if "银行" in stock_name or "保险" in stock_name or "证券" in stock_name else "其他"
                    except:
                        sector = "其他"
                    
                    stock_list.append({
                        'code': stock_code,
                        'name': stock_name,
                        'weight': weight,
                        'market_cap': market_cap,
                        'sector': sector
                    })
                    
                    print(f"已处理: {stock_code} {stock_name}")
                    time.sleep(0.1)  # 避免请求过快
                    
                except Exception as e:
                    print(f"处理股票 {stock_code} 时出错: {e}")
                    continue
            
            self.hs300_stocks = pd.DataFrame(stock_list)
            print(f"成功获取 {len(self.hs300_stocks)} 只股票信息")
            return True
            
        except Exception as e:
            print(f"获取沪深300成分股失败: {e}")
            return False
    
    def analyze_sectors(self):
        """分析板块分布"""
        if self.hs300_stocks is None:
            print("请先获取股票数据")
            return
        
        print("正在分析板块分布...")
        
        # 按板块分组
        sector_groups = self.hs300_stocks.groupby('sector')
        
        for sector, group in sector_groups:
            # 按市值排序
            sorted_group = group.sort_values('market_cap', ascending=False)
            
            self.sector_data[sector] = {
                'stocks': sorted_group,
                'count': len(sorted_group),
                'total_market_cap': sorted_group['market_cap'].sum(),
                'avg_market_cap': sorted_group['market_cap'].mean()
            }
        
        # 按板块股票数量排序
        self.sector_data = dict(sorted(self.sector_data.items(), 
                                      key=lambda x: x[1]['count'], 
                                      reverse=True))
        
        print(f"发现 {len(self.sector_data)} 个板块")
    
    def generate_html_report(self, filename="hs300_sector_analysis.html"):
        """生成HTML报告"""
        if not self.sector_data:
            print("请先分析板块数据")
            return
        
        print("正在生成HTML报告...")
        
        # 准备统计数据
        total_stocks = len(self.hs300_stocks)
        total_sectors = len(self.sector_data)
        total_market_cap = f"{self.hs300_stocks['market_cap'].sum():.2f}"
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 生成板块内容
        sector_content = ""
        for sector, data in self.sector_data.items():
            sector_content += f"""
            <div class="sector-section">
                <div class="sector-header">
                    <span class="sector-name">{sector}</span>
                    <span class="sector-count">{data['count']} 只股票 | 总市值: {data['total_market_cap']:.2f}亿</span>
                </div>
                <table class="stock-table">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>股票代码</th>
                            <th>股票名称</th>
                            <th>市值(亿元)</th>
                            <th>权重(%)</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for idx, (_, stock) in enumerate(data['stocks'].iterrows(), 1):
                sector_content += f"""
                        <tr>
                            <td>{idx}</td>
                            <td class="stock-code">{stock['code']}</td>
                            <td class="stock-name">{stock['name']}</td>
                            <td class="market-cap">{stock['market_cap']:.2f}</td>
                            <td>{stock['weight']:.2f}</td>
                        </tr>
                """
            
            sector_content += """
                    </tbody>
                </table>
            </div>
            """
        
        # 生成完整HTML
        html_content = self.html_template.format(
            total_stocks=total_stocks,
            total_sectors=total_sectors,
            total_market_cap=total_market_cap,
            update_time=update_time,
            sector_content=sector_content,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML报告已生成: {filename}")
        return filename
    
    def run_analysis(self):
        """运行完整分析流程"""
        print("开始沪深300板块分析...")
        
        # 1. 获取股票数据
        if not self.get_hs300_stocks():
            return False
        
        # 2. 分析板块分布
        self.analyze_sectors()
        
        # 3. 生成HTML报告
        filename = self.generate_html_report()
        
        print("分析完成！")
        return filename

def main():
    """主函数"""
    analyzer = HS300SectorAnalyzer()
    filename = analyzer.run_analysis()
    
    if filename:
        print(f"\n报告已生成: {filename}")
        print("请在浏览器中打开查看详细结果")
    else:
        print("分析失败，请检查网络连接和数据源")

if __name__ == "__main__":
    main() 