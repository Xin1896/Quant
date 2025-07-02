#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
哔哩哔哩视频下载器
支持下载视频、音频、弹幕等
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from urllib.parse import urlparse

class BilibiliDownloader:
    def __init__(self, output_dir="downloads"):
        """
        初始化下载器
        :param output_dir: 下载目录
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        self.check_dependencies()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"创建下载目录: {self.output_dir}")
    
    def check_dependencies(self):
        """检查依赖是否安装"""
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            print("✓ yt-dlp 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ yt-dlp 未安装，正在安装...")
            self.install_yt_dlp()
    
    def install_yt_dlp(self):
        """安装 yt-dlp"""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
            print("✓ yt-dlp 安装成功")
        except subprocess.CalledProcessError:
            print("❌ yt-dlp 安装失败，请手动安装: pip install yt-dlp")
            sys.exit(1)
    
    def download_video(self, url, quality="best", format="mp4"):
        """
        下载视频
        :param url: 视频URL
        :param quality: 视频质量 (best, worst, 720p, 1080p等)
        :param format: 输出格式
        """
        if not self.is_valid_bilibili_url(url):
            print("❌ 无效的哔哩哔哩URL")
            return False
        
        print(f"开始下载: {url}")
        print(f"质量: {quality}, 格式: {format}")
        
        # 构建下载命令
        cmd = [
            "yt-dlp",
            "--output", f"{self.output_dir}/%(title)s.%(ext)s",
            "--format", f"best[height<={quality}]" if quality.isdigit() else quality,
            "--merge-output-format", format,
            "--write-subtitle",  # 下载字幕
            "--write-auto-sub",  # 下载自动生成的字幕
            "--embed-subs",      # 嵌入字幕
            "--write-description",  # 下载视频描述
            "--write-thumbnail",    # 下载封面
            "--write-comments",     # 下载评论
            "--write-info-json",    # 下载视频信息
            "--cookies-from-browser", "chrome",  # 使用Chrome的cookies
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ 下载完成！")
                return True
            else:
                print(f"❌ 下载失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 下载出错: {str(e)}")
            return False
    
    def download_audio(self, url, quality="best"):
        """
        下载音频
        :param url: 视频URL
        :param quality: 音频质量
        """
        if not self.is_valid_bilibili_url(url):
            print("❌ 无效的哔哩哔哩URL")
            return False
        
        print(f"开始下载音频: {url}")
        
        cmd = [
            "yt-dlp",
            "--output", f"{self.output_dir}/%(title)s.%(ext)s",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", quality,
            "--cookies-from-browser", "chrome",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ 音频下载完成！")
                return True
            else:
                print(f"❌ 音频下载失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 音频下载出错: {str(e)}")
            return False
    
    def download_playlist(self, url, quality="best", format="mp4"):
        """
        下载播放列表
        :param url: 播放列表URL
        :param quality: 视频质量
        :param format: 输出格式
        """
        print(f"开始下载播放列表: {url}")
        
        cmd = [
            "yt-dlp",
            "--output", f"{self.output_dir}/%(playlist_title)s/%(title)s.%(ext)s",
            "--format", f"best[height<={quality}]" if quality.isdigit() else quality,
            "--merge-output-format", format,
            "--yes-playlist",  # 确认下载播放列表
            "--cookies-from-browser", "chrome",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ 播放列表下载完成！")
                return True
            else:
                print(f"❌ 播放列表下载失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 播放列表下载出错: {str(e)}")
            return False
    
    def get_video_info(self, url):
        """
        获取视频信息
        :param url: 视频URL
        """
        if not self.is_valid_bilibili_url(url):
            print("❌ 无效的哔哩哔哩URL")
            return None
        
        print(f"获取视频信息: {url}")
        
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--cookies-from-browser", "chrome",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return info
            else:
                print(f"❌ 获取视频信息失败: {result.stderr}")
                return None
        except Exception as e:
            print(f"❌ 获取视频信息出错: {str(e)}")
            return None
    
    def is_valid_bilibili_url(self, url):
        """检查是否为有效的哔哩哔哩URL"""
        parsed = urlparse(url)
        return "bilibili.com" in parsed.netloc
    
    def list_available_formats(self, url):
        """
        列出可用的格式
        :param url: 视频URL
        """
        if not self.is_valid_bilibili_url(url):
            print("❌ 无效的哔哩哔哩URL")
            return
        
        print(f"获取可用格式: {url}")
        
        cmd = [
            "yt-dlp",
            "--list-formats",
            "--cookies-from-browser", "chrome",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("可用格式:")
                print(result.stdout)
            else:
                print(f"❌ 获取格式失败: {result.stderr}")
        except Exception as e:
            print(f"❌ 获取格式出错: {str(e)}")

def main():
    """主函数"""
    print("=" * 50)
    print("哔哩哔哩视频下载器")
    print("=" * 50)
    
    # 创建下载器实例
    downloader = BilibiliDownloader()
    
    while True:
        print("\n请选择操作:")
        print("1. 下载视频")
        print("2. 下载音频")
        print("3. 下载播放列表")
        print("4. 获取视频信息")
        print("5. 列出可用格式")
        print("6. 退出")
        
        choice = input("\n请输入选择 (1-6): ").strip()
        
        if choice == "1":
            url = input("请输入视频URL: ").strip()
            quality = input("请输入视频质量 (best/worst/720p/1080p等，默认best): ").strip() or "best"
            format_type = input("请输入输出格式 (mp4/mkv等，默认mp4): ").strip() or "mp4"
            downloader.download_video(url, quality, format_type)
        
        elif choice == "2":
            url = input("请输入视频URL: ").strip()
            quality = input("请输入音频质量 (0-9，默认0): ").strip() or "0"
            downloader.download_audio(url, quality)
        
        elif choice == "3":
            url = input("请输入播放列表URL: ").strip()
            quality = input("请输入视频质量 (best/worst/720p/1080p等，默认best): ").strip() or "best"
            format_type = input("请输入输出格式 (mp4/mkv等，默认mp4): ").strip() or "mp4"
            downloader.download_playlist(url, quality, format_type)
        
        elif choice == "4":
            url = input("请输入视频URL: ").strip()
            info = downloader.get_video_info(url)
            if info:
                print("\n视频信息:")
                print(f"标题: {info.get('title', 'N/A')}")
                print(f"时长: {info.get('duration', 'N/A')}秒")
                print(f"上传者: {info.get('uploader', 'N/A')}")
                print(f"观看次数: {info.get('view_count', 'N/A')}")
                print(f"点赞数: {info.get('like_count', 'N/A')}")
        
        elif choice == "5":
            url = input("请输入视频URL: ").strip()
            downloader.list_available_formats(url)
        
        elif choice == "6":
            print("感谢使用！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main() 