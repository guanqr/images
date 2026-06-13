# -*- coding: utf-8 -*-
"""摄影作品批量处理 — 入口与调度"""
import sys
import os

# 修复 Windows 控制台乱码
if sys.platform.startswith("win"):
    try:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    except Exception:
        pass

from exif_utils import get_exif_info
from toml_utils import parse_toml_entries, write_toml
from watermark import process_image


def batch_process(input_dir, output_dir, toml_path=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    src_to_entry = {}
    if toml_path:
        for entry in parse_toml_entries(toml_path):
            src_to_entry[entry["src"]] = entry

    skipped = 0
    processed = 0
    for f in sorted(os.listdir(input_dir)):
        if not f.lower().endswith((".jpg", ".jpeg")):
            continue

        input_path = os.path.join(input_dir, f)
        output_path = os.path.join(output_dir, f)

        needs_reprocess = True
        if os.path.exists(output_path):
            if os.path.getmtime(output_path) >= os.path.getmtime(input_path):
                needs_reprocess = False

        exif_info = get_exif_info(input_path)

        if needs_reprocess:
            try:
                process_image(input_path, output_path, exif_info)
                photo_year = exif_info.get("time", "")[:4]
                print(f"✅ 处理完成：{f}  {photo_year if photo_year else ''}")
                processed += 1
            except Exception as e:
                print(f"❌ 处理失败：{f}  {e}")
        else:
            skipped += 1

        if toml_path:
            src = f"/images/photos/{f}"
            if src not in src_to_entry:
                src_to_entry[src] = {
                    "src": src,
                    "alt": "",
                    "category": "",
                    "focus": exif_info["focus"],
                    "iso": exif_info["iso"],
                    "aperture": exif_info["aperture"],
                    "shutter": exif_info["shutter"],
                    "time": exif_info["time"],
                    "place": "",
                    "location": "",
                }

    if toml_path:
        write_toml(toml_path, list(src_to_entry.values()))

    print(f"📊 本次处理 {processed} 张，跳过 {skipped} 张（未变化）")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_FOLDER = os.path.join(BASE_DIR, "original_photos")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "output_photos")
    TOML_PATH = os.path.join(BASE_DIR, "photo.toml")

    print("===== 开始处理 =====")
    batch_process(INPUT_FOLDER, OUTPUT_FOLDER, toml_path=TOML_PATH)
    print("===== 全部完成 =====")
