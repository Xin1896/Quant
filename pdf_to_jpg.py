import os
from pdf2image import convert_from_path
from datetime import datetime

def convert_pdf_to_jpg(pdf_path, output_dir=None):
    """
    将PDF文件转换为JPG图片
    :param pdf_path: PDF文件路径
    :param output_dir: 输出目录，默认为PDF所在目录
    :return: 生成的图片文件路径列表
    """
    # 如果没有指定输出目录，使用PDF所在目录
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 转换PDF为图片
    print(f"正在转换PDF: {pdf_path}")
    images = convert_from_path(pdf_path)
    
    # 保存图片
    image_paths = []
    for i, image in enumerate(images):
        # 生成输出文件路径
        output_path = os.path.join(output_dir, f"{pdf_name}_{timestamp}_page_{i+1}.jpg")
        
        # 保存图片
        image.save(output_path, 'JPEG')
        image_paths.append(output_path)
        print(f"已保存图片: {output_path}")
    
    print(f"转换完成！共生成 {len(image_paths)} 张图片")
    return image_paths

if __name__ == "__main__":
    # 获取用户输入
    pdf_path = input("请输入PDF文件路径: ").strip()
    
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print("错误：PDF文件不存在！")
    else:
        # 获取输出目录
        output_dir = input("请输入输出目录（直接回车使用PDF所在目录）: ").strip()
        if not output_dir:
            output_dir = None
        
        try:
            # 转换PDF
            convert_pdf_to_jpg(pdf_path, output_dir)
        except Exception as e:
            print(f"转换过程中发生错误: {str(e)}") 