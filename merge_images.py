from PIL import Image
import os
from datetime import datetime

def merge_images(image_paths, output_path=None):
    """
    将多张图片垂直拼接成一张长图
    :param image_paths: 图片路径列表
    :param output_path: 输出文件路径，默认为当前目录下的merged_image_时间戳.jpg
    :return: 输出文件路径
    """
    # 如果没有指定输出路径，生成默认路径
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f'merged_image_{timestamp}.jpg'
    
    # 打开所有图片
    images = [Image.open(path) for path in image_paths]
    
    # 获取所有图片的宽度
    widths = [img.width for img in images]
    # 获取所有图片的高度
    heights = [img.height for img in images]
    
    # 计算新图片的尺寸
    max_width = max(widths)
    total_height = sum(heights)
    
    # 创建新图片
    merged_image = Image.new('RGB', (max_width, total_height), (255, 255, 255))
    
    # 垂直拼接图片
    y_offset = 0
    for img in images:
        # 如果图片宽度小于最大宽度，居中放置
        if img.width < max_width:
            x_offset = (max_width - img.width) // 2
        else:
            x_offset = 0
        
        # 粘贴图片
        merged_image.paste(img, (x_offset, y_offset))
        y_offset += img.height
    
    # 保存拼接后的图片
    merged_image.save(output_path, quality=95)
    print(f"图片已保存到: {output_path}")
    
    # 关闭所有图片
    for img in images:
        img.close()
    
    return output_path

if __name__ == "__main__":
    # 获取用户输入
    print("请输入要合并的图片路径（多个路径用空格分隔）：")
    paths_input = input().strip()
    
    # 分割路径
    image_paths = [path.strip() for path in paths_input.split() if path.strip()]
    
    # 检查文件是否存在
    valid_paths = []
    for path in image_paths:
        if os.path.exists(path):
            valid_paths.append(path)
        else:
            print(f"警告：文件不存在 - {path}")
    
    if not valid_paths:
        print("错误：没有输入有效的图片路径！")
    else:
        # 获取输出路径
        output_path = input("请输入输出文件路径（直接回车使用默认路径）: ").strip()
        if not output_path:
            output_path = None
        
        try:
            # 合并图片
            merge_images(valid_paths, output_path)
        except Exception as e:
            print(f"合并过程中发生错误: {str(e)}") 