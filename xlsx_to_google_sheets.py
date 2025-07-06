#!/usr/bin/env python3
"""
XLSX to Google Sheets Converter
将本地XLSX文件转换为Google Sheets在线文档
"""

import os
import sys
import json
from typing import List, Dict, Any
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Google Sheets API 配置
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'

class XlsxToGoogleSheets:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Google Sheets API 认证"""
        creds = None
        
        # 尝试从token文件加载凭据
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # 如果没有有效凭据，进行OAuth2认证
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    print(f"❌ 错误: 找不到 {CREDENTIALS_FILE} 文件")
                    print("请按照以下步骤获取Google Sheets API凭据:")
                    print("1. 访问 https://console.cloud.google.com/")
                    print("2. 创建新项目或选择现有项目")
                    print("3. 启用 Google Sheets API")
                    print("4. 创建服务账号或OAuth2凭据")
                    print("5. 下载凭据文件并重命名为 credentials.json")
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 保存凭据到文件
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('sheets', 'v4', credentials=creds)
        print("✅ Google Sheets API 认证成功")
    
    def read_xlsx_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """读取XLSX文件的所有工作表"""
        try:
            # 读取所有工作表
            excel_file = pd.ExcelFile(file_path)
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets_data[sheet_name] = df
            
            print(f"✅ 成功读取XLSX文件: {file_path}")
            print(f"   包含 {len(sheets_data)} 个工作表: {', '.join(sheets_data.keys())}")
            return sheets_data
            
        except Exception as e:
            print(f"❌ 读取XLSX文件失败: {e}")
            sys.exit(1)
    
    def create_google_sheet(self, title: str) -> str:
        """创建新的Google Sheets文档"""
        try:
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            print(f"✅ 创建Google Sheets文档成功")
            print(f"   文档ID: {spreadsheet_id}")
            print(f"   访问链接: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            
            return spreadsheet_id
            
        except HttpError as e:
            print(f"❌ 创建Google Sheets文档失败: {e}")
            sys.exit(1)
    
    def dataframe_to_sheets_format(self, df: pd.DataFrame) -> List[List[Any]]:
        """将DataFrame转换为Google Sheets格式"""
        # 处理NaN值
        df = df.fillna('')
        
        # 转换为列表格式
        data = [df.columns.tolist()]  # 添加列标题
        data.extend(df.values.tolist())
        
        return data
    
    def update_sheet(self, spreadsheet_id: str, sheet_name: str, data: List[List[Any]]):
        """更新Google Sheets中的工作表"""
        try:
            # 准备更新请求
            range_name = f"{sheet_name}!A1"
            
            # 清除现有内容
            self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=sheet_name
            ).execute()
            
            # 更新数据
            body = {
                'values': data
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ 更新工作表 '{sheet_name}' 成功")
            print(f"   更新了 {result.get('updatedCells')} 个单元格")
            
        except HttpError as e:
            print(f"❌ 更新工作表 '{sheet_name}' 失败: {e}")
    
    def format_sheet(self, spreadsheet_id: str, sheet_name: str, data: List[List[Any]]):
        """格式化工作表（设置列宽、样式等）"""
        try:
            if not data or len(data) < 2:
                return
            
            # 获取数据范围
            max_col = len(data[0])
            max_row = len(data)
            
            # 设置列宽
            requests = []
            for col in range(max_col):
                requests.append({
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': 0,  # 假设是第一个工作表
                            'dimension': 'COLUMNS',
                            'startIndex': col,
                            'endIndex': col + 1
                        }
                    }
                })
            
            # 设置标题行样式
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1,
                        'startColumnIndex': 0,
                        'endColumnIndex': max_col
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': 0.9,
                                'green': 0.9,
                                'blue': 0.9
                            },
                            'textFormat': {
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            })
            
            # 应用格式
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            print(f"✅ 格式化工作表 '{sheet_name}' 成功")
            
        except HttpError as e:
            print(f"⚠️  格式化工作表失败: {e}")
    
    def convert_xlsx_to_google_sheets(self, xlsx_path: str, sheet_title: str = None):
        """主转换函数"""
        # 读取XLSX文件
        sheets_data = self.read_xlsx_file(xlsx_path)
        
        # 生成Google Sheets标题
        if not sheet_title:
            base_name = os.path.splitext(os.path.basename(xlsx_path))[0]
            sheet_title = f"{base_name} - 转换自XLSX"
        
        # 创建Google Sheets文档
        spreadsheet_id = self.create_google_sheet(sheet_title)
        
        # 转换每个工作表
        for sheet_name, df in sheets_data.items():
            print(f"\n📊 处理工作表: {sheet_name}")
            
            # 转换数据格式
            data = self.dataframe_to_sheets_format(df)
            
            # 更新Google Sheets
            self.update_sheet(spreadsheet_id, sheet_name, data)
            
            # 格式化工作表
            self.format_sheet(spreadsheet_id, sheet_name, data)
        
        print(f"\n🎉 转换完成!")
        print(f"📋 Google Sheets链接: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
        return spreadsheet_id

def main():
    """主函数"""
    print("🚀 XLSX to Google Sheets 转换器")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python xlsx_to_google_sheets.py <xlsx文件路径> [Google Sheets标题]")
        print("示例: python xlsx_to_google_sheets.py data.xlsx '我的数据表'")
        sys.exit(1)
    
    xlsx_path = sys.argv[1]
    sheet_title = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 检查文件是否存在
    if not os.path.exists(xlsx_path):
        print(f"❌ 错误: 文件不存在 - {xlsx_path}")
        sys.exit(1)
    
    # 检查文件扩展名
    if not xlsx_path.lower().endswith(('.xlsx', '.xls')):
        print(f"❌ 错误: 不支持的文件格式 - {xlsx_path}")
        print("支持的文件格式: .xlsx, .xls")
        sys.exit(1)
    
    try:
        # 创建转换器实例
        converter = XlsxToGoogleSheets()
        
        # 执行转换
        converter.convert_xlsx_to_google_sheets(xlsx_path, sheet_title)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 转换过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 