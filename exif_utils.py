# -*- coding: utf-8 -*-
"""EXIF 信息提取"""
from PIL import Image
from PIL.ExifTags import TAGS
from fractions import Fraction


def get_exif_info(image_path):
    """从 EXIF 中提取：focus, iso, aperture, shutter, time"""
    info = {
        "focus": "",
        "iso": "",
        "aperture": "",
        "shutter": "",
        "time": "",
    }
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if not exif_data:
            return info

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            try:
                if tag == "FocalLength":
                    info["focus"] = str(round(float(value)))
                elif tag == "ISOSpeedRatings":
                    info["iso"] = str(int(value))
                elif tag == "FNumber":
                    v = float(value)
                    if v == int(v):
                        info["aperture"] = str(int(v))
                    else:
                        info["aperture"] = f"{v:.1f}"
                elif tag == "ExposureTime":
                    v = float(value)
                    if v >= 1:
                        info["shutter"] = str(int(v)) if v == int(v) else f"{v:.1f}"
                    else:
                        frac = Fraction(v).limit_denominator(4000)
                        info["shutter"] = f"{frac.numerator}/{frac.denominator}"
                elif tag == "DateTimeOriginal":
                    if value and len(str(value)) >= 10:
                        info["time"] = str(value)[:10].replace(":", "-")
                elif tag == "DateTime" and not info["time"]:
                    if value and len(str(value)) >= 10:
                        info["time"] = str(value)[:10].replace(":", "-")
            except Exception:
                pass
    except Exception:
        pass
    return info


def get_year(exif_info):
    """从 exif_info 的 time 字段提取年份"""
    t = exif_info.get("time", "")
    return t[:4] if len(t) >= 4 else ""
