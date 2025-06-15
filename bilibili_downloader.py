import os
from datetime import datetime
import yt_dlp

def download_bilibili_video(url, output_path=None):
    """
    下载B站视频
    :param url: B站视频URL
    :param output_path: 输出文件路径，默认为当前目录下的视频标题.mp4
    :return: 下载的文件路径
    """
    # 设置下载选项
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',  # B站特定格式
        'outtmpl': output_path if output_path else '%(title)s.%(ext)s',  # 使用视频标题作为文件名
        'cookiesfrombrowser': ('chrome',),  # 使用Chrome浏览器的cookies
    }
    
    try:
        # 下载视频
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("正在下载视频...")
            ydl.download([url])
            
            # 获取实际保存的文件名
            if not output_path:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"{video_title}_{timestamp}.mp4"
            
            print(f"视频已下载到: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"下载过程中发生错误: {str(e)}")
        return None

if __name__ == "__main__":
    # 获取用户输入
    video_url = input("请输入B站视频URL: ").strip()
    
    if not video_url:
        print("错误：请输入有效的视频URL！")
    else:
        # 获取输出路径
        output_path = input("请输入输出文件路径（直接回车使用默认路径）: ").strip()
        if not output_path:
            output_path = None
        
        # 下载视频
        download_bilibili_video(video_url, output_path) 