# XLSX to Google Sheets 转换器使用说明

## 功能概述

这个工具可以将本地的XLSX/XLS文件转换为Google Sheets在线文档，支持：
- 多工作表转换
- 自动格式化
- 批量处理
- 图形界面操作

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements_xlsx_converter.txt
```

### 2. 获取Google Sheets API凭据

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google Sheets API：
   - 进入 "API和服务" > "库"
   - 搜索 "Google Sheets API"
   - 点击启用
4. 创建OAuth2凭据：
   - 进入 "API和服务" > "凭据"
   - 点击 "创建凭据" > "OAuth 2.0 客户端ID"
   - 选择应用类型为 "桌面应用"
   - 下载凭据文件
5. 将下载的凭据文件重命名为 `credentials.json` 并放在项目目录中

## 使用方法

### 命令行版本

```bash
# 基本用法
python xlsx_to_google_sheets.py data.xlsx

# 指定Google Sheets标题
python xlsx_to_google_sheets.py data.xlsx "我的数据表"

# 查看帮助
python xlsx_to_google_sheets.py
```

### 图形界面版本

```bash
python xlsx_to_google_sheets_gui.py
```

GUI版本提供以下功能：
- 文件选择器
- 实时日志显示
- 进度条
- 一键认证
- 转换状态监控

## 功能特性

### 1. 多工作表支持
- 自动读取XLSX文件中的所有工作表
- 保持原有工作表名称
- 支持复杂的数据结构

### 2. 数据格式保持
- 保留列标题
- 处理空值（NaN）
- 保持数据类型

### 3. 自动格式化
- 自动调整列宽
- 标题行加粗和背景色
- 优化显示效果

### 4. 安全认证
- OAuth2认证流程
- 凭据本地保存
- 自动刷新令牌

## 文件结构

```
├── xlsx_to_google_sheets.py          # 命令行版本
├── xlsx_to_google_sheets_gui.py      # 图形界面版本
├── requirements_xlsx_converter.txt   # Python依赖
├── credentials.json                  # Google API凭据（需要手动获取）
├── token.pickle                      # 认证令牌（自动生成）
└── XLSX转换器使用说明.md             # 本说明文件
```

## 常见问题

### Q: 认证失败怎么办？
A: 确保已正确下载并重命名 `credentials.json` 文件，且Google Sheets API已启用。

### Q: 转换大文件时很慢？
A: 大文件转换需要时间，请耐心等待。可以考虑分批处理。

### Q: 支持哪些文件格式？
A: 支持 `.xlsx` 和 `.xls` 格式的Excel文件。

### Q: 转换后的Google Sheets在哪里？
A: 转换完成后会显示Google Sheets的访问链接，也可以在你的Google Drive中找到。

### Q: 如何处理包含公式的Excel文件？
A: 当前版本会将公式转换为计算结果值。如需保留公式，需要手动处理。

## 高级用法

### 批量转换

```bash
# 使用脚本批量转换多个文件
for file in *.xlsx; do
    python xlsx_to_google_sheets.py "$file"
done
```

### 自定义格式化

可以修改代码中的 `format_sheet` 方法来自定义Google Sheets的样式：

```python
def format_sheet(self, spreadsheet_id: str, sheet_name: str, data: List[List[Any]]):
    # 自定义样式设置
    requests = [
        {
            'repeatCell': {
                'range': {...},
                'cell': {
                    'userEnteredFormat': {
                        'backgroundColor': {'red': 0.8, 'green': 0.9, 'blue': 1.0},
                        'textFormat': {'bold': True, 'fontSize': 12}
                    }
                }
            }
        }
    ]
    # 应用格式...
```

## 注意事项

1. **API配额限制**: Google Sheets API有使用配额限制，大量转换时请注意。
2. **文件大小**: 建议单个文件不超过10MB，行数不超过100万行。
3. **网络连接**: 需要稳定的网络连接来访问Google API。
4. **权限管理**: 转换后的Google Sheets默认只有创建者可以访问，需要手动设置共享权限。

## 技术支持

如果遇到问题，请检查：
1. Python版本是否为3.7+
2. 所有依赖是否正确安装
3. Google API凭据是否正确配置
4. 网络连接是否正常

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本的XLSX到Google Sheets转换
- 提供命令行和GUI两种界面
- 支持多工作表和自动格式化 