# -*- coding: utf-8 -*-
import sys
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 修复 Windows 乱码
if sys.platform.startswith('win'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    except:
        pass


def get_region_brightness(img, region_h=100):
    """截取图片底部区域，计算平均亮度 0~255"""
    w, h = img.size
    # 截取底部长条区域
    crop_box = (0, h - region_h, w, h)
    crop_img = img.crop(crop_box).convert("L")
    pixels = list(crop_img.getdata())
    avg_bright = sum(pixels) / len(pixels)
    return avg_bright

def add_watermark(img, text="Guanqr  Photography", opacity=0.85):
    img = img.convert("RGBA")

    # ========== 修复透明度：新建独立透明图层 ==========
    watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_size = 28

    try:
        # Windows/Mac/Linux 通用的专业英文字体
        font = ImageFont.truetype("TheNautigal-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("Arial", font_size)
        except:
            font = ImageFont.truetype("Helvetica", font_size)

    # 兼容新旧Pillow 文字宽高
    try:
        _, _, w, h = draw.textbbox((0, 0), text, font=font)
    except:
        w, h = draw.textsize(text, font=font)


    # 底部居中位置
    x = (img.width - w) // 2
    y = img.height - h - 15


    # 检测底部明暗，自动选颜色
    bright = get_region_brightness(img, region_h=100)
    alpha = int(255 * opacity)
    # 阈值：大于127偏亮→黑字；小于127偏暗→白字
    if bright > 127:
        fill = (0, 0, 0, alpha)      # 黑色
    else:
        fill = (255, 255, 255, alpha)# 白色

    draw.text((x, y), text, font=font, fill=fill)

    # 合并图层
    img = Image.alpha_composite(img, watermark_layer)

    return img.convert("RGB")

def process_image(input_path, output_path, target_long_side=1500, max_size_kb=200):
    try:
        with Image.open(input_path) as img:
            img = img.convert('RGB')
            original_w, original_h = img.size

            # 缩放长边1280
            if original_w >= original_h:
                new_w = target_long_side
                new_h = int(target_long_side * original_h / original_w)
            else:
                new_h = target_long_side
                new_w = int(target_long_side * original_w / original_h)

            img_resized = img.resize((new_w, new_h), Image.LANCZOS)

            # 加水印
            img_watermark = add_watermark(img_resized)

            # 压缩到200KB
            quality = 95
            while quality > 10:
                buf = BytesIO()
                img_watermark.save(buf, 'JPEG', quality=quality, optimize=True)
                if buf.tell() / 1024 <= max_size_kb:
                    break
                quality -= 5

            with open(output_path, 'wb') as f:
                f.write(buf.getvalue())

        print(f"✅ 处理完成：{os.path.basename(input_path)}")

    except Exception as e:
        print(f"❌ 处理失败：{str(e)}")

def batch_process(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for f in os.listdir(input_dir):
        if f.lower().endswith(('.jpg', '.jpeg')):
            process_image(os.path.join(input_dir, f), os.path.join(output_dir, f))

if __name__ == "__main__":
    INPUT_FOLDER = "E:\预处理摄影作品\处理图片"
    OUTPUT_FOLDER = "E:\预处理摄影作品\处理图片\处理后照片"
    
    print("===== 开始处理 =====")
    batch_process(INPUT_FOLDER, OUTPUT_FOLDER)
    print("===== 全部完成 =====")