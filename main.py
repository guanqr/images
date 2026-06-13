# -*- coding: utf-8 -*-
import sys
import os
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS, GPSTAGS
from io import BytesIO

# 修复 Windows 乱码
if sys.platform.startswith('win'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    except:
        pass

def get_photo_year(image_path):
    """优先读取拍摄时间DateTimeOriginal，无则使用DateTime，都没有返回空"""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return ""

        year = ""
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            # 优先原始拍摄时间
            if tag == "DateTimeOriginal":
                if value and len(value) >= 4:
                    year = value[:4]
                    break
        # 拍摄时间不存在，再取普通日期时间
        if not year:
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "DateTime":
                    if value and len(value) >= 4:
                        year = value[:4]
                        break
        return year
    except:
        return ""

def get_region_brightness(img, region_h=100):
    """截取图片底部区域，计算平均亮度 0~255"""
    w, h = img.size
    crop_box = (0, h - region_h, w, h)
    crop_img = img.crop(crop_box).convert("L")
    # 兼容新旧Pillow：优先用新API，降级兼容旧版本
    try:
        pixels = list(crop_img.get_flattened_data())
    except AttributeError:
        pixels = list(crop_img.getdata())
    avg_bright = sum(pixels) / len(pixels)
    return avg_bright

def add_watermark(img, text="Guanqr Photography", opacity=0.6, photo_year=""):
    img = img.convert("RGBA")

    # 修复透明度：新建独立透明图层
    watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_size = 24

    font_path = os.path.join(os.path.dirname(__file__), "fonts", "NotoSans-Bold.ttf")
    try:
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 自动添加 @年份
    if photo_year and len(photo_year) == 4:
        final_text = f"{text} @ {photo_year}"
    else:
        final_text = text

    # 兼容新旧Pillow 文字宽高
    try:
        _, _, w, h = draw.textbbox((0, 0), final_text, font=font)
    except:
        w, h = draw.textsize(final_text, font=font)

    # 底部居中位置
    x = (img.width - w) // 2
    y = img.height - h - 25

    # 检测底部明暗，自动选颜色
    bright = get_region_brightness(img, region_h=100)
    alpha = int(255 * opacity)
    if bright > 127:
        fill = (0, 0, 0, alpha)      # 黑色水印
    else:
        fill = (255, 255, 255, alpha)# 白色水印

    draw.text((x, y), final_text, font=font, fill=fill)

    # 合并图层
    img = Image.alpha_composite(img, watermark_layer)
    return img.convert("RGB")

def process_image(input_path, output_path, target_long_side=1920, max_size_kb=400):
    try:
        # 先读取拍摄年份
        photo_year = get_photo_year(input_path)

        with Image.open(input_path) as img:
            img = img.convert('RGB')
            original_w, original_h = img.size

            # 缩放长边
            if original_w >= original_h:
                new_w = target_long_side
                new_h = int(target_long_side * original_h / original_w)
            else:
                new_h = target_long_side
                new_w = int(target_long_side * original_w / original_h)

            img_resized = img.resize((new_w, new_h), Image.LANCZOS)

            # 加水印（自动带年份）
            img_watermark = add_watermark(img_resized, photo_year=photo_year)

            # 循环压缩至限定大小
            quality = 95
            while quality > 10:
                buf = BytesIO()
                img_watermark.save(buf, 'JPEG', quality=quality, optimize=True)
                if buf.tell() / 1024 <= max_size_kb:
                    break
                quality -= 5

            with open(output_path, 'wb') as f:
                f.write(buf.getvalue())

        print(f"✅ 处理完成：{os.path.basename(input_path)}  {photo_year if photo_year else ''}")

    except Exception as e:
        print(f"❌ 处理失败：{str(e)}")

def batch_process(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    skipped = 0
    processed = 0
    for f in sorted(os.listdir(input_dir)):
        if not f.lower().endswith(('.jpg', '.jpeg')):
            continue

        input_path = os.path.join(input_dir, f)
        output_path = os.path.join(output_dir, f)

        # 输出已存在且输入未变化 → 跳过
        if os.path.exists(output_path):
            input_mtime = os.path.getmtime(input_path)
            output_mtime = os.path.getmtime(output_path)
            if output_mtime >= input_mtime:
                skipped += 1
                continue

        process_image(input_path, output_path)
        processed += 1

    print(f"📊 本次处理 {processed} 张，跳过 {skipped} 张（未变化）")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_FOLDER = os.path.join(BASE_DIR, "original_photos")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "output_photos")
    
    print("===== 开始处理 =====")
    batch_process(INPUT_FOLDER, OUTPUT_FOLDER)
    print("===== 全部完成 =====")