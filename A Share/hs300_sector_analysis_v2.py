#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沪深300板块分析工具 V2
分析沪深300成分股的板块分布，按市值排序显示结果
使用更准确的行业分类
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import time
import warnings
import re
warnings.filterwarnings('ignore')

class HS300SectorAnalyzerV2:
    def __init__(self):
        self.hs300_stocks = None
        self.sector_data = {}
        self.industry_mapping = {
            '银行': '金融',
            '保险': '金融', 
            '证券': '金融',
            '信托': '金融',
            '基金': '金融',
            '期货': '金融',
            '地产': '房地产',
            '房地产': '房地产',
            '建筑': '房地产',
            '建材': '房地产',
            '钢铁': '原材料',
            '有色金属': '原材料',
            '化工': '原材料',
            '石油': '能源',
            '煤炭': '能源',
            '电力': '公用事业',
            '燃气': '公用事业',
            '水务': '公用事业',
            '汽车': '汽车',
            '新能源': '新能源',
            '光伏': '新能源',
            '风电': '新能源',
            '医药': '医药生物',
            '生物': '医药生物',
            '医疗': '医药生物',
            '器械': '医药生物',
            '科技': '科技',
            '软件': '科技',
            '互联网': '科技',
            '通信': '科技',
            '电子': '科技',
            '半导体': '科技',
            '芯片': '科技',
            '消费': '消费',
            '食品': '消费',
            '饮料': '消费',
            '家电': '消费',
            '零售': '消费',
            '旅游': '消费',
            '航空': '交通运输',
            '港口': '交通运输',
            '物流': '交通运输',
            '铁路': '交通运输',
            '公路': '交通运输',
            '农业': '农业',
            '养殖': '农业',
            '种植': '农业',
            '机械': '工业',
            '装备': '工业',
            '制造': '工业',
            '军工': '国防军工',
            '航天': '国防军工',
            '船舶': '国防军工'
        }
        
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
            max-width: 1400px;
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
        .sector-overview {
            margin: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .sector-overview h3 {
            margin: 0 0 20px 0;
            color: #333;
        }
        .sector-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .sector-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .sector-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .sector-name {
            font-weight: bold;
            color: #333;
        }
        .sector-count {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .sector-stats {
            font-size: 0.9em;
            color: #666;
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
        .sector-name-large {
            font-size: 1.3em;
            font-weight: bold;
        }
        .sector-summary {
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
        .weight {
            color: #007bff;
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
            .sector-grid { grid-template-columns: 1fr; }
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
        
        <div class="sector-overview">
            <h3>板块概览</h3>
            <div class="sector-grid">
                {sector_overview}
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
    
    def classify_sector(self, stock_name, stock_info):
        """根据股票名称和信息分类板块"""
        # 首先尝试从股票信息中获取行业
        sector = "其他"
        
        # 根据股票名称匹配行业
        for keyword, industry in self.industry_mapping.items():
            if keyword in stock_name:
                sector = industry
                break
        
        # 如果还是"其他"，尝试从股票详细信息中获取
        if sector == "其他" and not stock_info.empty:
            for _, info_row in stock_info.iterrows():
                item_str = str(info_row['item']).lower()
                value_str = str(info_row['value']).lower()
                
                if '行业' in item_str or '板块' in item_str:
                    for keyword, industry in self.industry_mapping.items():
                        if keyword in value_str:
                            sector = industry
                            break
                    break
        
        return sector
    
    def get_hs300_stocks(self):
        """获取沪深300成分股列表"""
        try:
            print("正在获取沪深300成分股列表...")
            # 获取沪深300成分股
            hs300_df = ak.index_stock_cons_weight_csindex(symbol="000300")
            
            # 获取股票基本信息
            stock_list = []
            total_stocks = len(hs300_df)
            
            for idx, (_, row) in enumerate(hs300_df.iterrows(), 1):
                try:
                    stock_code = row['成分券代码']
                    stock_name = row['成分券名称']
                    weight = row['权重']
                    
                    print(f"处理进度: {idx}/{total_stocks} - {stock_code} {stock_name}")
                    
                    # 获取股票详细信息
                    try:
                        stock_info = ak.stock_individual_info_em(symbol=stock_code)
                    except:
                        stock_info = pd.DataFrame()
                    
                    # 提取市值信息
                    market_cap = 0
                    
                    if not stock_info.empty:
                        # 查找市值信息
                        for _, info_row in stock_info.iterrows():
                            item_str = str(info_row['item'])
                            if '总市值' in item_str or '市值' in item_str:
                                try:
                                    value_str = str(info_row['value'])
                                    # 处理不同格式的市值
                                    if '亿' in value_str:
                                        market_cap = float(re.sub(r'[^\d.]', '', value_str))
                                    elif '万' in value_str:
                                        market_cap = float(re.sub(r'[^\d.]', '', value_str)) / 10000
                                    else:
                                        # 假设是元为单位
                                        market_cap = float(re.sub(r'[^\d.]', '', value_str)) / 100000000
                                    break
                                except:
                                    continue
                    
                    # 分类板块
                    sector = self.classify_sector(stock_name, stock_info)
                    
                    stock_list.append({
                        'code': stock_code,
                        'name': stock_name,
                        'weight': weight,
                        'market_cap': market_cap,
                        'sector': sector
                    })
                    
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
                'avg_market_cap': sorted_group['market_cap'].mean(),
                'total_weight': sorted_group['weight'].sum()
            }
        
        # 按板块股票数量排序
        self.sector_data = dict(sorted(self.sector_data.items(), 
                                      key=lambda x: x[1]['count'], 
                                      reverse=True))
        
        print(f"发现 {len(self.sector_data)} 个板块")
        
        # 打印板块统计
        for sector, data in self.sector_data.items():
            print(f"{sector}: {data['count']}只股票, 总市值{data['total_market_cap']:.2f}亿, 权重{data['total_weight']:.2f}%")
    
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
        
        # 生成板块概览
        sector_overview = ""
        for sector, data in self.sector_data.items():
            sector_overview += f"""
            <div class="sector-card">
                <div class="sector-card-header">
                    <span class="sector-name">{sector}</span>
                    <span class="sector-count">{data['count']}</span>
                </div>
                <div class="sector-stats">
                    总市值: {data['total_market_cap']:.2f}亿<br>
                    平均市值: {data['avg_market_cap']:.2f}亿<br>
                    权重: {data['total_weight']:.2f}%
                </div>
            </div>
            """
        
        # 生成板块详细内容
        sector_content = ""
        for sector, data in self.sector_data.items():
            sector_content += f"""
            <div class="sector-section">
                <div class="sector-header">
                    <span class="sector-name-large">{sector}</span>
                    <span class="sector-summary">
                        {data['count']} 只股票 | 总市值: {data['total_market_cap']:.2f}亿 | 权重: {data['total_weight']:.2f}%
                    </span>
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
                            <td class="weight">{stock['weight']:.2f}</td>
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
            sector_overview=sector_overview,
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
    analyzer = HS300SectorAnalyzerV2()
    filename = analyzer.run_analysis()
    
    if filename:
        print(f"\n报告已生成: {filename}")
        print("请在浏览器中打开查看详细结果")
    else:
        print("分析失败，请检查网络连接和数据源")

if __name__ == "__main__":
    main() 