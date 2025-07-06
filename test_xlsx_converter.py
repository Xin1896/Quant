import pandas as pd
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# Scopes needed for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def authenticate_google_sheets():
    """Authenticate and return Google Sheets service object"""
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # Download from Google Cloud Console
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('sheets', 'v4', credentials=creds)

def xlsx_to_google_sheets(xlsx_file_path, sheet_name="Converted Sheet"):
    """Convert Excel file to Google Sheets"""
    # Read Excel file with explicit engine specification
    try:
        # 首先尝试使用 openpyxl 引擎（适用于 .xlsx 文件）
        df = pd.read_excel(xlsx_file_path, engine='openpyxl')
    except Exception as e1:
        try:
            # 如果失败，尝试使用 xlrd 引擎（适用于 .xls 文件）
            df = pd.read_excel(xlsx_file_path, engine='xlrd')
        except Exception as e2:
            try:
                # 最后尝试使用 odf 引擎（适用于 .ods 文件）
                df = pd.read_excel(xlsx_file_path, engine='odf')
            except Exception as e3:
                print(f"无法读取文件 {xlsx_file_path}")
                print(f"openpyxl 错误: {e1}")
                print(f"xlrd 错误: {e2}")
                print(f"odf 错误: {e3}")
                print("请确保文件格式正确，并且已安装相应的引擎库")
                return None
    
    print(f"成功读取 Excel 文件，共 {len(df)} 行数据")
    
    # Authenticate
    try:
        service = authenticate_google_sheets()
    except Exception as e:
        print(f"Google Sheets 认证失败: {e}")
        print("请确保 credentials.json 文件存在且配置正确")
        return None
    
    # Create a new Google Sheet
    spreadsheet = {
        'properties': {
            'title': sheet_name
        }
    }
    
    try:
        spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                  fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
    except Exception as e:
        print(f"创建 Google Sheet 失败: {e}")
        return None
    
    # Convert DataFrame to list of lists for Google Sheets
    values = [df.columns.tolist()] + df.values.tolist()
    
    # Update the sheet with data
    body = {
        'values': values
    }
    
    try:
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range='A1',
            valueInputOption='RAW', body=body).execute()
        
        print(f'成功创建 Google Sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}')
        print(f'更新了 {result.get("updatedCells")} 个单元格')
        return spreadsheet_id
    except Exception as e:
        print(f"更新 Google Sheet 数据失败: {e}")
        return None

# Usage
if __name__ == "__main__":
    result = xlsx_to_google_sheets('/Users/jimmy/Documents/QuantitationTrade/100_Live_Trades_Record_Form.xlsx', 'My Converted Sheet')
    if result:
        print("转换完成！")
    else:
        print("转换失败！")