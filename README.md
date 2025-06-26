# 视频文字提取工具

这个工具可以从视频中提取文字，并将结果保存为Markdown格式。

## 安装步骤

1. 安装Python依赖：
```bash
# 使用conda安装
conda install opencv
conda install pytesseract
conda install moviepy

# 或者使用pip安装
pip install -r requirements.txt
```

2. 安装Tesseract OCR（Mac系统）：
```bash
# 安装Tesseract
brew install tesseract

# 安装中文语言包
brew install tesseract-lang
```

## 使用方法

1. 运行程序：
```bash
python video_to_text.py
```

2. 按提示输入：
   - 视频文件路径
   - 输出Markdown文件路径

## 功能特点

- 支持中文和英文识别
- 按时间戳保存识别结果
- 输出格式为Markdown
- 每秒提取一帧进行识别

## 注意事项

1. 确保视频文件路径正确
2. 确保已安装所有必要的依赖
3. 视频处理时间取决于视频长度
4. 文字识别效果取决于视频质量和文字清晰度 

conda activate quant_trade