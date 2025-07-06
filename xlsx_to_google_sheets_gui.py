#!/usr/bin/env python3
"""
XLSX to Google Sheets Converter - GUI版本
带图形界面的XLSX文件转换为Google Sheets工具
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from datetime import datetime
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

class XlsxToGoogleSheetsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XLSX to Google Sheets 转换器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.service = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="XLSX to Google Sheets 转换器", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="选择XLSX文件", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="文件路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_btn = ttk.Button(file_frame, text="浏览", command=self.browse_file)
        self.browse_btn.grid(row=0, column=2)
        
        # Google Sheets标题
        title_frame = ttk.LabelFrame(main_frame, text="Google Sheets设置", padding="10")
        title_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        
        ttk.Label(title_frame, text="文档标题:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.sheet_title_var = tk.StringVar()
        self.title_entry = ttk.Entry(title_frame, textvariable=self.sheet_title_var, width=50)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 认证状态
        auth_frame = ttk.LabelFrame(main_frame, text="认证状态", padding="10")
        auth_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.auth_status_var = tk.StringVar(value="未认证")
        self.auth_status_label = ttk.Label(auth_frame, textvariable=self.auth_status_var, 
                                          foreground="red")
        self.auth_status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.auth_btn = ttk.Button(auth_frame, text="认证Google账户", command=self.authenticate)
        self.auth_btn.grid(row=0, column=1, padx=(20, 0))
        
        # 转换按钮
        self.convert_btn = ttk.Button(main_frame, text="开始转换", command=self.start_conversion,
                                     state="disabled")
        self.convert_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置主框架的行权重
        main_frame.rowconfigure(6, weight=1)
        
        # 绑定事件
        self.file_path_var.trace('w', self.on_file_path_change)
        self.sheet_title_var.trace('w', self.on_title_change)
        
    def browse_file(self):
        """浏览并选择XLSX文件"""
        file_path = filedialog.askopenfilename(
            title="选择XLSX文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            # 自动设置Google Sheets标题
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.sheet_title_var.set(f"{base_name} - 转换自XLSX")
    
    def on_file_path_change(self, *args):
        """文件路径改变时的处理"""
        self.update_convert_button()
    
    def on_title_change(self, *args):
        """标题改变时的处理"""
        self.update_convert_button()
    
    def update_convert_button(self):
        """更新转换按钮状态"""
        has_file = bool(self.file_path_var.get().strip())
        has_title = bool(self.sheet_title_var.get().strip())
        is_authenticated = self.service is not None
        
        if has_file and has_title and is_authenticated:
            self.convert_btn.config(state="normal")
        else:
            self.convert_btn.config(state="disabled")
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def authenticate(self):
        """Google Sheets API 认证"""
        def auth_thread():
            try:
                self.log_message("开始Google Sheets API认证...")
                self.auth_status_var.set("认证中...")
                self.auth_status_label.config(foreground="orange")
                self.root.update_idletasks()
                
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
                            self.log_message("❌ 错误: 找不到 credentials.json 文件")
                            self.log_message("请按照以下步骤获取Google Sheets API凭据:")
                            self.log_message("1. 访问 https://console.cloud.google.com/")
                            self.log_message("2. 创建新项目或选择现有项目")
                            self.log_message("3. 启用 Google Sheets API")
                            self.log_message("4. 创建OAuth2凭据")
                            self.log_message("5. 下载凭据文件并重命名为 credentials.json")
                            
                            self.auth_status_var.set("认证失败")
                            self.auth_status_label.config(foreground="red")
                            return
                        
                        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    # 保存凭据到文件
                    with open(TOKEN_FILE, 'wb') as token:
                        pickle.dump(creds, token)
                
                self.service = build('sheets', 'v4', credentials=creds)
                
                self.log_message("✅ Google Sheets API 认证成功")
                self.auth_status_var.set("已认证")
                self.auth_status_label.config(foreground="green")
                self.update_convert_button()
                
            except Exception as e:
                self.log_message(f"❌ 认证失败: {e}")
                self.auth_status_var.set("认证失败")
                self.auth_status_label.config(foreground="red")
        
        # 在新线程中执行认证
        threading.Thread(target=auth_thread, daemon=True).start()
    
    def start_conversion(self):
        """开始转换过程"""
        def conversion_thread():
            try:
                self.convert_btn.config(state="disabled")
                self.progress_var.set(0)
                
                xlsx_path = self.file_path_var.get().strip()
                sheet_title = self.sheet_title_var.get().strip()
                
                self.log_message("🚀 开始转换XLSX文件...")
                self.progress_var.set(10)
                
                # 读取XLSX文件
                self.log_message(f"📖 读取文件: {xlsx_path}")
                excel_file = pd.ExcelFile(xlsx_path)
                sheets_data = {}
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(xlsx_path, sheet_name=sheet_name)
                    sheets_data[sheet_name] = df
                
                self.log_message(f"✅ 成功读取XLSX文件")
                self.log_message(f"   包含 {len(sheets_data)} 个工作表: {', '.join(sheets_data.keys())}")
                self.progress_var.set(30)
                
                # 创建Google Sheets文档
                self.log_message("📄 创建Google Sheets文档...")
                spreadsheet = {
                    'properties': {
                        'title': sheet_title
                    }
                }
                
                spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
                spreadsheet_id = spreadsheet.get('spreadsheetId')
                
                self.log_message("✅ 创建Google Sheets文档成功")
                self.log_message(f"   文档ID: {spreadsheet_id}")
                self.log_message(f"   访问链接: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                self.progress_var.set(50)
                
                # 转换每个工作表
                total_sheets = len(sheets_data)
                for i, (sheet_name, df) in enumerate(sheets_data.items()):
                    self.log_message(f"📊 处理工作表: {sheet_name}")
                    
                    # 转换数据格式
                    df = df.fillna('')
                    data = [df.columns.tolist()]
                    data.extend(df.values.tolist())
                    
                    # 更新Google Sheets
                    range_name = f"{sheet_name}!A1"
                    body = {'values': data}
                    
                    result = self.service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_name,
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                    
                    self.log_message(f"✅ 更新工作表 '{sheet_name}' 成功")
                    self.log_message(f"   更新了 {result.get('updatedCells')} 个单元格")
                    
                    # 更新进度
                    progress = 50 + (i + 1) / total_sheets * 40
                    self.progress_var.set(progress)
                
                self.progress_var.set(100)
                self.log_message("🎉 转换完成!")
                self.log_message(f"📋 Google Sheets链接: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                
                # 显示成功消息
                messagebox.showinfo("转换完成", 
                                  f"XLSX文件已成功转换为Google Sheets!\n\n"
                                  f"文档链接:\nhttps://docs.google.com/spreadsheets/d/{spreadsheet_id}")
                
            except Exception as e:
                self.log_message(f"❌ 转换过程中发生错误: {e}")
                messagebox.showerror("转换失败", f"转换过程中发生错误:\n{e}")
            finally:
                self.convert_btn.config(state="normal")
        
        # 在新线程中执行转换
        threading.Thread(target=conversion_thread, daemon=True).start()

def main():
    """主函数"""
    root = tk.Tk()
    app = XlsxToGoogleSheetsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 